"""Pipeline orchestrator — runs S0..S7 and assembles the Report.

Decision tree (mirrors QuinticMethods_v1.md):

    S0 parse/normalize -> S1 normal form -> S2 factor over Q
        |
        +-- reducible ----> roots of each factor (deg <= 4, classical
        |                   formulas via SymPy roots), gate, report
        |
        +-- irreducible -> S3 Galois group (SymPy; optional Sage
                            cross-check)
              |
              +-- solvable (C5/D5/F20) -> S4a radicals (F20 resolvent +
              |                           Lagrange resolvents), gate;
              |                           fallback to S4b if the gate
              |                           rejects every root
              +-- unsolvable (A5/S5) -- > S4b CRootOf exact forms, gate

    S5 numerical roots (always): mpmath Aberth + NumPy companion +
    Durand-Kerner
    S6 verification gate on every exact root
    S7 report (Markdown/JSON)
"""

from __future__ import annotations

import time
from typing import List, Optional, Sequence, Union

import sympy as sp

from .errors import PipelineError
from .factor import factor_quintic
from .galois import classify
from .input import parse_input
from .normalform import depress_quintic
from .numeric import numeric_roots
from .radicals import radical_roots
from .report import Report, StepTrace
from .special import special_forms
from .verify import VerificationGate

__all__ = ["simulate"]


def _root_entry(root, numeric_str: str, verdict) -> dict:
    return {
        "expr": str(root),
        "numeric": numeric_str,
        "verified": bool(verdict.ok),
        "detail": verdict.detail,
    }


def _factor_roots(f: sp.Poly, x) -> List[sp.Expr]:
    """Roots of a degree-<=4 factor (classical formulas), or CRootOf fallback."""
    rd = sp.roots(f.as_expr(), x)
    if rd and sum(rd.values()) == f.degree():
        out: List[sp.Expr] = []
        for r, m in rd.items():
            out.extend([r] * m)
        return out
    return [sp.CRootOf(f.as_expr(), x, index=k) for k in range(f.degree())]


def _special_dict(f: sp.Poly, x) -> dict:
    s = special_forms(f)
    return {
        "crootofs": list(s.crootofs),
        "bring_radical": s.bring_radical,
        "klein": s.klein,
        "notes": list(s.notes),
    }


def simulate(
    coeffs: Union[Sequence, sp.Expr],
    *,
    use_sage: bool = False,
    sage_timeout: int = 120,
    symbol: Union[sp.Symbol, str, None] = None,
) -> Report:
    """Run the full quintic-solver pipeline and return a Report.

    Parameters
    ----------
    coeffs:
        Descending rational coefficient list [a5..a0] or a SymPy
        expression in one variable.
    use_sage:
        Enable the optional Sage-in-Docker Galois-group cross-check.
    sage_timeout:
        Per-call timeout for the Sage container (seconds).
    """
    traces: List[StepTrace] = []
    warnings: List[str] = []

    def stage(s: str, name: str, fn, detail: str):
        t0 = time.perf_counter()
        result = fn()
        traces.append(StepTrace(
            stage=s, name=name, detail=detail,
            duration=time.perf_counter() - t0,
        ))
        return result

    def replace_last_trace(name: str, detail: str) -> None:
        last = traces[-1]
        traces[-1] = StepTrace(
            stage=last.stage, name=name, detail=detail, duration=last.duration,
        )

    # ---------------- S0 ----------------
    parsed = stage(
        "S0", "input & squarefree decomposition",
        lambda: parse_input(coeffs, symbol=symbol),
        "parse -> monic primitive ZZ polynomial; squarefree check via "
        "gcd(f, f') (exact).",
    )
    f = parsed.poly
    x = f.gen
    warnings.extend(parsed.warnings)

    # ---------------- S1 ----------------
    nf = stage(
        "S1", "normal form",
        lambda: depress_quintic(f),
        "depressed quintic (x = y - a4/5); palindromic detection + "
        "quadratic-in-t reduction; Bring-Jerrard skipped (v1 policy).",
    )

    # ---------------- S2 ----------------
    fr = stage(
        "S2", "factorization over Q",
        lambda: factor_quintic(f),
        "rational-root test (exact divisor enumeration) then Zassenhaus "
        "(SymPy factor_list: GF(p) + Hensel + Mignotte; no LLL).",
    )

    # ---------------- S5 (numeric, always available for the gate) ------
    t0 = time.perf_counter()
    nr = numeric_roots(f, dps=50)
    traces.append(StepTrace(
        stage="S5", name="numerical roots",
        detail=(
            "mpmath Aberth (50 digits) + NumPy companion-matrix "
            f"cross-check (numpy_match={nr.numpy_match}) + Durand-Kerner "
            f"({nr.durand_iterations} iterations, "
            f"converged={nr.n_converged})."
        ),
        duration=time.perf_counter() - t0,
    ))
    if not nr.numpy_match:
        warnings.append(
            "NumPy companion-matrix cross-check did NOT agree with "
            "Aberth to 1e-8 — inspect the roots."
        )

    gate = VerificationGate()
    group = None
    sage_result = None
    special = None
    method = None
    exact_roots: List[sp.Expr] = []

    if fr.reducible:
        # ---------------- reducible path ----------------
        method = "reducible"
        for fac, m in fr.factorization:
            exact_roots.extend(_factor_roots(fac, x) * m)
        # safeguard: the factor-root count must be exactly 5
        if len(exact_roots) != f.degree():
            exact_roots = [
                sp.CRootOf(f.as_expr(), x, index=k) for k in range(f.degree())
            ]
            warnings.append(
                "factor-based root assembly produced the wrong count; "
                "fell back to CRootOf forms for the whole polynomial."
            )
        stage(
            "S4", "reducible: roots of factors",
            lambda: None,
            "each factor has degree <= 4 -> classical radical formulas "
            f"(SymPy roots); {len(exact_roots)} roots with multiplicity.",
        )
    else:
        # ---------------- irreducible path ----------------
        g = stage(
            "S3", "Galois group",
            lambda: classify(f),
            "SymPy galois_group (Cohen Alg 6.3.9 quintic hybrid).",
        )
        group = g
        replace_last_trace("Galois group", g.method)
        if use_sage:
            from .sage_bridge import classify_with_sage
            sage_result = stage(
                "S3", "Sage cross-check (Docker)",
                lambda: classify_with_sage(
                    [int(c) for c in f.all_coeffs()], timeout=sage_timeout
                ),
                "optional Sage-in-Docker galois_group cross-check.",
            )
            replace_last_trace(
                "Sage cross-check (Docker)",
                f"status={sage_result.status}; "
                f"{sage_result.detail} ({sage_result.duration:.1f}s)",
            )
            if sage_result.status == "ok" and sage_result.name != g.name:
                warnings.append(
                    f"CONFLICT: SymPy says {g.name}, Sage says "
                    f"{sage_result.name} — exact roots still reported "
                    "with CRootOf forms; trust the numerics."
                )

        if g.solvable:
            rr = stage(
                "S4", "radicals (solvable quintic)",
                lambda: radical_roots(f),
                "SymPy roots_quintic (F20 resolvent + Lagrange resolvents).",
            )
            replace_last_trace(
                "radicals (solvable quintic)",
                f"{rr.method} F20 resolvent: `{rr.f20_resolvent.as_expr()}` "
                f"(integer root theta = {rr.f20_integer_root}).",
            )
            if rr.solvable:
                method = "radicals"
                exact_roots = list(rr.roots)
            else:
                warnings.append(
                    "Theory says solvable but SymPy produced no radical "
                    "form; using CRootOf exact forms instead."
                )
                special = _special_dict(f, x)
                method = "special"
                exact_roots = list(special["crootofs"])
        else:
            method = "special"
            special = _special_dict(f, x)
            exact_roots = list(special["crootofs"])
            stage(
                "S4", "special forms (unsolvable)",
                lambda: None,
                "CRootOf exact algebraic numbers (Vincent isolation); "
                "Bring-radical notation"
                + (" present" if special["bring_radical"] else " n/a")
                + "; Klein icosahedral solution is a documented stub "
                  "(no open-source implementation).",
            )

    # ---------------- S6 gate ----------------
    # adaptive cross-match tolerance: machine precision when the numeric
    # reference is the NumPy fallback (multiple roots), 50 digits otherwise
    match_tol = 6 if nr.source == "numpy-fallback" else 25
    verdicts = stage(
        "S6", "verification gate",
        lambda: gate.run(f, exact_roots, nr.abarth, match_tol=match_tol),
        f"residual < 1e-30 (40 digits) + cross-match vs {nr.source} to "
        f"1e-{match_tol} for {len(exact_roots)} exact roots.",
    )

    roots: List[dict] = []
    for root, v in zip(exact_roots, verdicts):
        if not v.ok:
            # replace with the CRootOf form closest to the failed value,
            # and re-verify once
            num_mp = complex(sp.N(root, 30))
            best, bestd = None, None
            for k in range(f.degree()):
                ck = sp.CRootOf(f.as_expr(), x, index=k)
                d = abs(complex(sp.N(ck, 30)) - num_mp)
                if bestd is None or d < bestd:
                    best, bestd = ck, d
            cr = best
            v2 = VerificationGate.check_root(f, cr)
            roots.append(_root_entry(cr, str(sp.N(cr, 15)), v2))
            warnings.append(
                f"exact root failed the gate ({v.detail}); replaced by "
                f"CRootOf form (verified={v2.ok})."
            )
        else:
            roots.append(_root_entry(root, str(sp.N(root, 15)), v))

    verified = all(r["verified"] for r in roots)
    if not verified:
        warnings.append(
            "one or more roots could not be verified — see per-root "
            "details; numeric values remain valid (Aberth, 50 digits)."
        )

    stage(
        "S7", "report",
        lambda: None,
        "assembled Markdown/JSON report with step trace and timings.",
    )

    return Report(
        input=str(f.as_expr()),
        method=method or "unknown",
        verified=verified,
        reducible=fr.reducible,
        group=group,
        normal_form=nf,
        factor_result=fr,
        roots=roots,
        warnings=warnings,
        step_traces=traces,
        sage=None if sage_result is None else {
            "status": sage_result.status,
            "name": sage_result.name,
            "group_number": sage_result.group_number,
            "order": sage_result.order,
            "solvable": sage_result.solvable,
            "label": sage_result.label,
            "detail": sage_result.detail,
            "duration": sage_result.duration,
        },
        special=special,
        numeric_source=nr.source,
        durand_iterations=nr.durand_iterations,
    )
