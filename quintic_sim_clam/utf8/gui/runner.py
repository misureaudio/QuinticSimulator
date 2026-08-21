"""Command wrapper: coefficients -> expression, command building, subprocess run.

This module contains no tkinter import so it is unit-testable headlessly.
It also contains no sympy/numpy import: coefficient parsing uses
``fractions.Fraction`` (exact rationals, which is all the pipeline accepts),
and the actual computation happens in the wrapped subprocess.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "RunResult",
    "parse_coeff",
    "format_polynomial",
    "format_coeff_list",
    "clean_env",
    "build_command",
    "run_command",
]


# ---------------------------------------------------------------------------
# coefficients -> polynomial
# ---------------------------------------------------------------------------
def parse_coeff(text: str) -> Fraction:
    """Parse one coefficient box into an exact rational.

    Accepts ints, decimals, fractions ("1/2") and scientific notation
    ("1e3"). Raises ValueError on garbage.
    """
    t = text.strip().replace(",", ".")
    if not t:
        return Fraction(0)
    try:
        return Fraction(t)
    except (ValueError, ZeroDivisionError):
        pass
    try:
        return Fraction(float(t)).limit_denominator(10**12)
    except (ValueError, OverflowError):
        raise ValueError(f"not a number: {text!r}") from None


def _num(v: Fraction) -> str:
    """Render a rational for the CLI: '2', '-3', '1/2' (all sympy-parseable)."""
    return str(v)


def format_polynomial(coeffs: Sequence[Fraction]) -> Tuple[Optional[str], Optional[str]]:
    """Build a sympy-parseable expression from 6 descending coeffs [c5..c0].

    Returns ``(expr, error)`` — exactly one of the two is None. The output
    matches the CLI's accepted syntax, e.g.::

        [1, -2, -3, 0, 0, -1]  ->  "x^5 - 2*x^4 - 3*x^3 - 1"
    """
    if len(coeffs) != 6:
        return None, "expected 6 coefficients (c5..c0)"
    if all(c == 0 for c in coeffs):
        return None, "all coefficients are zero (not a polynomial)"
    if coeffs[0] == 0:
        return None, "c5 is zero — the polynomial is not degree 5 (quintic required)"

    parts: List[str] = []
    first = True
    for i, c in enumerate(coeffs):
        k = 5 - i
        if c == 0:
            continue
        neg, mag = c < 0, abs(c)
        if k == 0:
            body = _num(mag)
        elif mag == 1:
            body = "x" if k == 1 else f"x^{k}"
        else:
            body = f"{_num(mag)}*x" if k == 1 else f"{_num(mag)}*x^{k}"
        if first:
            parts.append(("-" + body) if neg else body)
            first = False
        else:
            parts.append(f"{'-' if neg else '+'} {body}")
    return " ".join(parts), None


def format_coeff_list(coeffs: Sequence[Fraction]) -> str:
    """Robust comma-list form the CLI also accepts: '1,-2,-3,0,0,-1'."""
    return ",".join(_num(c) for c in coeffs)


# ---------------------------------------------------------------------------
# execution
# ---------------------------------------------------------------------------
@dataclass
class RunResult:
    ok: bool
    stdout: str
    stderr: str
    returncode: int
    duration: float
    command: str
    timed_out: bool = False


def clean_env() -> Dict[str, str]:
    """Copy of os.environ with hermes-agent PYTHONPATH entries removed.

    The agent shell exports a PYTHONPATH pointing at the hermes-agent venv,
    whose cp311 numpy shadows the project venv's cp313 numpy and crashes
    ``import numpy`` (ModuleNotFoundError: numpy._core._multiarray_umath).
    The wrapped command must run against the project venv only.
    """
    env = os.environ.copy()
    # BEGIN Hermes/qwen3.8 27b add
    env["PYTHONUTF8"] = "1"   # child must print UTF-8; we decode its stdout as UTF-8
    # END Hermes/qwen3.8 27b
    pp = env.get("PYTHONPATH", "")
    keep = [p for p in filter(None, pp.split(os.pathsep)) if "hermes-agent" not in p]
    env["PYTHONPATH"] = os.pathsep.join(keep)
    if not env["PYTHONPATH"]:
        env.pop("PYTHONPATH", None)
    return env


def build_command(template: str, poly: str, *, sage: bool = True) -> List[str]:
    """Substitute {poly} (shell-quoted) into the template and split to argv.

    When ``sage`` is False, any ``--sage`` flag in the template is dropped.
    """
    cmd = template.replace("{poly}", shlex.quote(poly))
    argv = shlex.split(cmd)
    if not sage and "--sage" in argv:
        argv = [a for a in argv if a != "--sage"]
    return argv


def run_command(
    template: str,
    poly: str,
    *,
    sage: bool = True,
    cwd: str,
    timeout: int = 300,
    proc_ref: Optional[Dict[str, Any]] = None,
) -> RunResult:
    """Run the wrapped command and return its markdown stdout + diagnostics.

    Uses Popen (not subprocess.run) so the caller can store the live handle
    in ``proc_ref`` and kill it (the GUI's Stop button).
    """
    argv = build_command(template, poly, sage=sage)
    env = clean_env()
    command = " ".join(shlex.quote(a) for a in argv)
    t0 = time.perf_counter()
    try:
        p = subprocess.Popen(
            argv,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, ValueError) as e:
        return RunResult(False, "", f"failed to start: {e}", -1,
                         time.perf_counter() - t0, command)
    if proc_ref is not None:
        proc_ref["p"] = p
    try:
        out, err = p.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        timed_out = True
    rc = p.returncode
    return RunResult(
        ok=(rc == 0),
        stdout=out or "",
        stderr=err or "",
        returncode=rc,
        duration=time.perf_counter() - t0,
        command=command,
        timed_out=timed_out,
    )
