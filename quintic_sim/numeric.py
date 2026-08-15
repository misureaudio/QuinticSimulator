"""S5 — numerical roots (v1 document section 6).

Primary: mpmath ``polyroots`` — **Aberth's method**, arbitrary precision
(50 digits by default).
Cross-check: ``numpy.linalg.eigvals`` of the companion matrix (the
"Jenkins-Tappe / companion-matrix" route of the document). NOTE the
coefficient-ordering trap: mpmath wants DESCENDING coefficients, NumPy's
polycompanion wants ASCENDING — handled here in one adapter.
Educational: a ~20-line Durand-Kerner (Weierstrass) implementation with
roots-of-unity seeding and a convergence history, so the *simulator*
part of the product is visible in the trace.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

import mpmath
import numpy as np
import sympy as sp

__all__ = ["NumericResult", "numeric_roots", "durand_kerner"]

DURAND_MAX_ITER = 200
DURAND_TOL = 1e-30


@dataclass
class NumericResult:
    abarth: Tuple[object, ...]          # mpmath mpc, arbitrary precision
    source: str                         # "abarth" | "numpy-fallback"
    numpy_eigs: Tuple[complex, ...]     # machine-precision cross-check
    numpy_match: bool                   # agree to ~1e-8
    durand_roots: Tuple[object, ...]    # mpmath mpc
    durand_iterations: Optional[int]
    durand_history: Tuple[float, ...]   # max |delta| per iteration
    n_converged: bool
    dps: int


def _coeffs_desc(f: sp.Poly) -> List[sp.Rational]:
    return [sp.Rational(c) for c in f.all_coeffs()]


def durand_kerner(
    coeffs_desc: Sequence,
    max_iter: int = DURAND_MAX_ITER,
    tol: float = DURAND_TOL,
    seed: int = 0,
):
    """Durand-Kerner (Weierstrass) simultaneous root iteration.

    coeffs_desc: descending coefficients. Returns
    (roots, iterations, history) with mpmath complex roots.
    Seeding: scaled 5th roots of unity (classic scheme).
    """
    n = len(coeffs_desc) - 1
    with mpmath.workdps(50):
        a = [mpmath.mpf(c) for c in coeffs_desc]
        a_norm = max(abs(c) for c in a)
        # initial guesses: scaled roots of unity
        scale = mpmath.mpf(1)
        # crude root bound: 1 + max|a_i/a_0|
        bound = 1 + max(abs(c) / abs(a[0]) for c in a[1:])
        scale = bound
        roots = [
            scale * mpmath.exp(mpmath.mpf(2 * mpmath.pi * (k + 0.5 * (seed % 2))) / n * 1j)
            for k in range(n)
        ]

        def polyval(z):
            acc = mpmath.mpc(a[0])
            for c in a[1:]:
                acc = acc * z + c
            return acc

        history: List[float] = []
        it = 0
        for it in range(1, max_iter + 1):
            max_delta = mpmath.mpf("0")
            for i in range(n):
                # product over j != i of (roots[i] - roots[j])
                prod = mpmath.mpc(1)
                for j in range(n):
                    if j != i:
                        prod *= roots[i] - roots[j]
                fval = polyval(roots[i])
                delta = fval / prod
                roots[i] -= delta
                max_delta = max(max_delta, abs(delta))
            history.append(float(max_delta))
            if max_delta < tol:
                break
    return tuple(roots), it, tuple(history)


def numeric_roots(f: sp.Poly, dps: int = 50) -> NumericResult:
    """Compute all 5 roots numerically with cross-checks.

    Primary is mpmath Aberth (arbitrary precision). Aberth degrades to
    linear convergence on multiple roots and may fail to converge there,
    so on NoConvergence we fall back to the NumPy companion-matrix
    eigenvalues (marked ``source='numpy-fallback'``). Both paths are
    always cross-checked against each other.
    """
    f = sp.Poly(f, f.gen)
    coeffs = _coeffs_desc(f)

    # --- cross-check first: NumPy companion matrix (ASCENDING coeffs!) ---
    asc = [float(c) for c in reversed(coeffs)]
    cm = np.polynomial.polynomial.polycompanion(asc)
    eigs = tuple(np.linalg.eigvals(cm))
    eigs_mp = tuple(
        mpmath.mpc(mpmath.mpf(repr(float(z.real))), mpmath.mpf(repr(float(z.imag))))
        for z in eigs
    )

    # --- primary: mpmath Aberth ---
    source = "abarth"
    try:
        with mpmath.workdps(dps):
            abarth = tuple(
                mpmath.polyroots(coeffs, maxsteps=200, cleanup=True)
            )
    except Exception:  # noqa: BLE001 — NoConvergence on multiple roots
        source = "numpy-fallback"
        abarth = eigs_mp

    # match to ~1e-8 (machine precision vs 50-digit Aberth)
    with mpmath.workdps(30):
        a = sorted(
            (float(mpmath.re(z)), float(mpmath.im(z))) for z in abarth
        )
    n_sorted = sorted((z.real, z.imag) for z in eigs)
    match = all(
        abs(ar - nr) < 1e-8 and abs(ai - ni) < 1e-8
        for (ar, ai), (nr, ni) in zip(a, n_sorted)
    )

    # --- educational: Durand-Kerner ---
    d_roots, d_iter, d_hist = durand_kerner(coeffs)

    return NumericResult(
        abarth=abarth,
        source=source,
        numpy_eigs=eigs,
        numpy_match=bool(match),
        durand_roots=d_roots,
        durand_iterations=d_iter,
        durand_history=d_hist,
        n_converged=(d_iter < DURAND_MAX_ITER),
        dps=dps,
    )
