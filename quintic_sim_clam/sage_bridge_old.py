"""Optional Sage-in-Docker cross-check for Galois-group classification.

Invokes the locally available ``sagemath/sagemath:latest`` image with the
verified protocol:

    docker run --rm --entrypoint /bin/bash sagemath/sagemath:latest -c \
        'sage << "SAGEEOF"
        <python/sage script that reads the embedded JSON data>
        SAGEEOF'

(the image's default entrypoint swallows file-argument invocations — the
``-c`` + heredoc form is the one verified to work).

Sage's ``f.galois_group()`` returns "Transitive group number N of
degree 5" with N = 1..5 mapping 1:1 to C5 / D5 / F20 / A5 / S5.
Internally Sage/PARI use Cohen's resolvent method plus table lookup; at
degree 5 Stauduhar's method (the general group-identification algorithm)
is not invoked.

The bridge is strictly optional: without Docker (or the image) it returns
status "skipped" and never raises. A timeout or malformed output returns
status "error". The pipeline treats a SymPy/Sage disagreement as CONFLICT
and falls back to numerics only.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import List, Optional, Sequence

__all__ = ["SageResult", "GROUP_NUMBER_TO_NAME", "docker_available",
           "classify_with_sage"]

IMAGE = "sagemath/sagemath:latest"

# Transitive group number (degree 5) -> canonical name
GROUP_NUMBER_TO_NAME = {1: "C5", 2: "D5", 3: "F20", 4: "A5", 5: "S5"}


@dataclass
class SageResult:
    status: str                     # ok | skipped | error
    name: Optional[str]             # C5|D5|F20|A5|S5 (ok only)
    group_number: Optional[int]
    order: Optional[int]
    solvable: Optional[bool]
    label: Optional[str]            # Sage's own label
    detail: str
    duration: float = 0.0


def docker_available() -> bool:
    """True if the docker CLI and the sagemath image are both present."""
    if shutil.which("docker") is None:
        return False
    try:
        r = subprocess.run(
            ["docker", "image", "inspect", IMAGE],
            capture_output=True, timeout=30,
        )
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def _sage_script(coeffs: Sequence[Sequence]) -> str:
    """Build the sage script (heredoc body) for the given coefficient lists."""
    data = json.dumps([list(c) for c in coeffs])
    return (
        "import json, re\n"
        f"data = {data}\n"
        "x = polygen(QQ)\n"
        "out = []\n"
        "for cs in data:\n"
        "    f = sum(c * x**i for i, c in enumerate(reversed(cs)))\n"
        "    G = f.galois_group()\n"
        '    m = re.search(r"number (\\d+)", str(G))\n'
        '    out.append({"label": str(G),\n'
        '                "number": int(m.group(1)) if m else None,\n'
        '                "order": int(G.order()),\n'
        '                "solvable": bool(G.is_solvable())})\n'
        "print(json.dumps(out))\n"
    )


def classify_with_sage(
    coeffs: Sequence,
    timeout: int = 120,
) -> SageResult:
    """Cross-check the Galois group of one quintic via Sage in Docker.

    ``coeffs`` is a descending coefficient list [a5..a0]. Never raises
    for environmental problems — returns a SageResult with status
    skipped/error instead.
    """
    if not docker_available():
        return SageResult(
            status="skipped",
            name=None,
            group_number=None,
            order=None,
            solvable=None,
            label=None,
            detail="docker CLI or sagemath/sagemath:latest image not available",
        )

    script = _sage_script([coeffs])
    body = f"sage << \"SAGEEOF\"\n{script}SAGEEOF"
    cmd = ["docker", "run", "--rm", "--entrypoint", "/bin/bash", IMAGE,
           "-c", body]

    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return SageResult(
            status="error", name=None, group_number=None, order=None,
            solvable=None, label=None,
            detail=f"sage container timed out after {timeout}s",
            duration=time.time() - t0,
        )
    except Exception as e:  # noqa: BLE001
        return SageResult(
            status="error", name=None, group_number=None, order=None,
            solvable=None, label=None, detail=f"docker invocation failed: {e}",
            duration=time.time() - t0,
        )

    # the JSON line may be prefixed by a "sage:" prompt; extract the array
    stdout = proc.stdout or ""
    m = re.search(r"\[.*\]", stdout, re.DOTALL)
    if m is None:
        return SageResult(
            status="error", name=None, group_number=None, order=None,
            solvable=None, label=None,
            detail=f"no JSON in sage output (rc={proc.returncode}): "
                   f"{stdout[-200:]!r}",
            duration=time.time() - t0,
        )
    try:
        rows = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return SageResult(
            status="error", name=None, group_number=None, order=None,
            solvable=None, label=None, detail=f"bad JSON: {e}",
            duration=time.time() - t0,
        )
    if not rows:
        return SageResult(
            status="error", name=None, group_number=None, order=None,
            solvable=None, label=None, detail="empty sage result",
            duration=time.time() - t0,
        )

    row = rows[0]
    number = row.get("number")
    name = GROUP_NUMBER_TO_NAME.get(number) if number is not None else None
    if name is None:
        return SageResult(
            status="error", name=None, group_number=number,
            order=row.get("order"), solvable=row.get("solvable"),
            label=row.get("label"),
            detail=f"unrecognized transitive group number: {number}",
            duration=time.time() - t0,
        )
    return SageResult(
        status="ok",
        name=name,
        group_number=number,
        order=row.get("order"),
        solvable=row.get("solvable"),
        label=row.get("label"),
        detail=f"sage: {row.get('label')}",
        duration=time.time() - t0,
    )
