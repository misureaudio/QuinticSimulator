"""S6 — verification gate (architecture-critical).

Every EXACT root (radical or CRootOf) is a hypothesis, never a proof.
Before it reaches the report it must pass two independent checks:

1. residual:  |f(r)| < 1e-30 * (1 + max|coeff| * max(1, |r|^5))
   evaluated at 40 working digits (mpmath, arbitrary precision);
2. cross-match: the numerically evaluated exact root must coincide with
   the S5 Aberth root (independent numerical method) to 1e-25.

Any failure yields a GateVerdict with ok=False and a detail string; the
pipeline replaces the offending exact root and records a WARNING.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

import mpmath
import sympy as sp

__all__ = ["GateVerdict", "VerificationGate"]

RESIDUAL_TOL = 30      # |f(r)| < 1e-30 (scaled)
MATCH_TOL = 25         # exact-vs-Aberth agreement to 1e-25
WORK_DPS = 40


def _sympy_to_mpc(z, dps: int) -> mpmath.mpc:
    """Convert a sympy number (Expr/Number) to a full-precision mpmath mpc."""
    z = sp.N(z, dps)
    re_ = sp.re(z)
    im_ = sp.im(z)

    def _conv(w) -> mpmath.mpf:
        w = sp.N(w, dps)
        if w.is_zero:
            return mpmath.mpf("0")
        # sympy and mpmath share the (sign, mant, exp, size) mpf tuple
        return mpmath.mpf(w._mpf_)

    return mpmath.mpc(_conv(re_), _conv(im_))


@dataclass
class GateVerdict:
    root: object
    ok: bool
    detail: str

    @staticmethod
    def check_root(f: sp.Poly, root, dps: int = WORK_DPS) -> "GateVerdict":
        """Residual check of a single exact root at high precision."""
        with mpmath.workdps(dps):
            r_mp = _sympy_to_mpc(root, dps)
            f_mp = sp.lambdify(f.gen, f.as_expr(), "mpmath")
            val = f_mp(r_mp)
            max_coeff = max(abs(int(c)) for c in f.all_coeffs())
            scale = mpmath.mpf(1) + max_coeff * max(abs(r_mp) ** 5, mpmath.mpf(1))
            tol = mpmath.mpf(10) ** (-RESIDUAL_TOL) * scale
            mag = abs(val)
            if mag < tol:
                return GateVerdict(
                    root=root,
                    ok=True,
                    detail=f"residual |f(r)| = {mag} < {tol} at {dps} digits",
                )
            return GateVerdict(
                root=root,
                ok=False,
                detail=(
                    f"residual FAILED: |f(r)| = {mag} >= {tol} at {dps} digits"
                ),
            )


@dataclass
class VerificationGate:
    """Runs the full gate: residual per root + Aberth cross-match."""

    def run(
        self,
        f: sp.Poly,
        exact_roots: Sequence,
        numeric_roots: Sequence,
        dps: int = WORK_DPS,
        match_tol: int = MATCH_TOL,
    ) -> List[GateVerdict]:
        """Run the gate. ``match_tol`` is an exponent: agreement to 10**-match_tol.

        Use 25 (the default) when the numeric reference is arbitrary-
        precision Aberth; use ~6 when the reference is machine-precision
        (NumPy companion fallback for multiple roots).
        """
        verdicts: List[GateVerdict] = []
        with mpmath.workdps(dps):
            num_mp = [mpmath.mpc(z) for z in numeric_roots]
            tol = mpmath.mpf(10) ** (-match_tol)
            for root in exact_roots:
                rv = GateVerdict.check_root(f, root, dps)
                # cross-match: nearest Aberth root
                r_mp = _sympy_to_mpc(root, dps)
                dists = sorted(
                    ((abs(r_mp - n), i) for i, n in enumerate(num_mp))
                )
                d, i = dists[0]
                if d >= tol:
                    rv = GateVerdict(
                        root=root,
                        ok=False,
                        detail=(
                            f"cross-match FAILED: nearest Aberth root "
                            f"#{i} at distance {d} >= {tol} "
                            f"(residual: {rv.detail})"
                        ),
                    )
                elif not rv.ok:
                    rv.detail = rv.detail + " (cross-match passed)"
                else:
                    rv.detail += f" | matches Aberth root #{i} (d={d})"
                verdicts.append(rv)
        return verdicts
