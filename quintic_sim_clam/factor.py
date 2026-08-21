"""S2 — factorization over Q (v1 document sections 1, 2, 5).

Algorithm (documented per the architecture plan):
1. Rational Root Theorem: candidates +- divisors(constant)/divisors(leading);
   each hit is factored out by exact division, repeated to exhaustion.
2. The remaining part is factored with SymPy's ``factor_list`` over QQ —
   the **Zassenhaus** algorithm: modular factorization over GF(p), Hensel
   lifting to p^k, and reconstruction under the Mignotte bound.
   (No LLL in this path; LLL-based reconstruction is PARI's approach and
   is only reachable via the optional Sage cross-check.)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import sympy as sp

__all__ = ["FactorResult", "rational_root_test", "factor_quintic"]


@dataclass
class FactorResult:
    rational_roots: Tuple[sp.Rational, ...]
    factorization: Tuple[Tuple[sp.Poly, int], ...]
    reducible: bool
    notes: Tuple[str, ...]


def _divisors(n: int) -> List[int]:
    """Positive divisors of n (n > 0)."""
    n = abs(int(n))
    out = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            out.append(i)
            if i != n // i:
                out.append(n // i)
        i += 1
    return out


def rational_root_test(f: sp.Poly) -> List[sp.Rational]:
    """Find all rational roots of a primitive integer polynomial.

    Rational Root Theorem: any rational root p/q (in lowest terms) has
    p | constant term and q | leading coefficient. Each candidate is
    evaluated exactly; no numeric approximation is involved.
    """
    f = sp.Poly(f, f.gen)
    coeffs = [int(c) for c in f.all_coeffs()]
    lead, const = coeffs[0], coeffs[-1]
    if const == 0:
        # zero is a root; strip the factor x (drop the trailing zero) and recurse
        rest = sp.Poly([c for c in coeffs[:-1]], f.gen, domain=sp.ZZ)
        return [sp.Rational(0)] + rational_root_test(rest)

    candidates = set()
    for p in _divisors(const):
        for q in _divisors(lead):
            candidates.add(sp.Rational(p, q))
            candidates.add(sp.Rational(-p, q))

    f_expr = f.as_expr()
    roots: List[sp.Rational] = []
    for r in sorted(candidates):
        if sp.simplify(f_expr.subs(f.gen, r)) == 0:
            roots.append(r)
    return roots


def factor_quintic(f: sp.Poly) -> FactorResult:
    """Factor a quintic over Q.

    Returns the full factorization with multiplicities, the rational roots
    found by the cheap exact test, and a reducibility flag.
    """
    f = sp.Poly(f, f.gen, domain=sp.ZZ)
    x = f.gen
    notes: List[str] = []

    # --- step 1: rational root test (exact) ---
    rroots = tuple(rational_root_test(f))
    remaining = f
    lin_mult: dict = {}
    for r in rroots:
        lin = sp.Poly(x - r, x, domain=sp.QQ)
        while True:
            q, rem = sp.div(remaining.as_expr(), lin.as_expr())
            if rem != 0:
                break
            remaining = sp.Poly(sp.expand(q), x, domain=sp.QQ)
            lin_mult[r] = lin_mult.get(r, 0) + 1
    notes.append(
        "Rational Root Theorem (exact divisor enumeration): "
        f"{len(rroots)} rational root(s) found."
    )

    # --- step 2: Zassenhaus on the remaining part ---
    remaining = sp.Poly(remaining, x, domain=sp.QQ)
    if remaining.degree() > 0:
        _, factors = remaining.factor_list()
        notes.append(
            "Zassenhaus (SymPy factor_list): GF(p) factor + Hensel lift + "
            "Mignotte reconstruction; no LLL in this path."
        )
    else:
        factors = []

    # combine linear rational factors with the Zassenhaus factors
    combined: List[Tuple[sp.Poly, int]] = []
    for r, m in sorted(lin_mult.items()):
        combined.append((sp.Poly(x - r, x, domain=sp.QQ), m))
    for fac, m in factors:
        combined.append((fac, m))

    reducible = (
        len(combined) > 1 or any(fac.degree() < 5 for fac, _ in combined)
    )
    return FactorResult(
        rational_roots=rroots,
        factorization=tuple(combined),
        reducible=reducible,
        notes=tuple(notes),
    )
