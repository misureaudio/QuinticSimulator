"""S3 — Galois-group computation and classification (v1 document section 1).

Primary algorithm: SymPy ``galois_group(f, by_name=True)``, which for
quintics runs ``_galois_group_degree_5_hybrid`` — Cohen's
*A Course in Computational Algebraic Number Theory*, **Alg 6.3.9**,
hybridized with root approximation:

1. sextic resolvent R51 with coefficient lookup; squarefreeness test;
   Tschirnhaus retries (bounded) if not squarefree;
2. R51 irreducible  ->  G = A5 if disc(f) is a square, else S5;
3. R51 squarefree but reducible  ->  G <= M20; disc(f) not a square -> M20;
4. otherwise: integer root of R51, then the quadratic resolvent R2 and
   the squareness of disc(R2) split C5 from D5.

The discriminant is computed exactly (resultant of f and f'); its
squareness is a factorint parity check. For degree 5, group
*identification* degenerates to a 5-row table (order + A5 membership) —
no LLL and no Stauduhar are involved (Stauduhar is PARI/Sage's
higher-degree machinery).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from typing import Optional, Tuple

import sympy as sp

from .errors import PipelineError

__all__ = ["GroupResult", "GROUP_TABLE", "classify"]


# Canonical classification table: the exactly 5 conjugacy classes of
# transitive subgroups of S5 (verified by enumerating all subgroups).
# "F20" is what SymPy calls M20 (Frobenius group AGL(1,5)).
GROUP_TABLE = {
    "C5":  {"order": 5,   "in_A5": True,  "solvable": True},
    "D5":  {"order": 10,  "in_A5": True,  "solvable": True},
    "F20": {"order": 20,  "in_A5": False, "solvable": True},
    "A5":  {"order": 60,  "in_A5": True,  "solvable": False},
    "S5":  {"order": 120, "in_A5": False, "solvable": False},
}

# SymPy's enum values -> canonical names
_SYMPY_NAME = {
    "C5": "C5",
    "D5": "D5",
    "M20": "F20",
    "A5": "A5",
    "S5": "S5",
}


@dataclass
class GroupResult:
    name: str                      # C5 | D5 | F20 | A5 | S5
    order: int
    in_A5: bool
    solvable: bool
    discriminant: int
    disc_square: bool
    method: str                    # human-readable algorithm description


def _disc_square(d: int) -> bool:
    """Exact squareness test for a positive integer discriminant."""
    if d < 0:
        # odd-degree polynomials have real roots; disc < 0 is possible for
        # quintics only if ... actually quintic disc can be negative.
        # A negative number is never a square in Q.
        return False
    r = isqrt(d)
    return r * r == d


def classify(f: sp.Poly) -> GroupResult:
    """Compute and classify the Galois group of an irreducible quintic.

    Raises
    ------
    PipelineError
        If ``f`` is not an irreducible quintic over Q (SymPy's
        galois_group requires irreducible univariate ZZ/QQ input).
    """
    f = sp.Poly(f, f.gen)
    if f.degree() != 5:
        raise PipelineError(
            f"expected an irreducible quintic, got degree {f.degree()}"
        )
    if not f.is_irreducible:
        raise PipelineError(
            "Galois-group classification requires an IRREDUCIBLE quintic; "
            "factor the polynomial first (S2)"
        )

    # ensure ZZ domain (SymPy's galois_group wants ZZ or QQ)
    f = sp.Poly(f, f.gen, domain=sp.ZZ)

    disc = int(f.discriminant())
    disc_sq = _disc_square(disc)

    try:
        G, alt = sp.galois_group(f, by_name=True)
    except Exception as e:  # noqa: BLE001
        raise PipelineError(f"Galois-group computation failed: {e}") from e

    sym_name = getattr(G, "value", str(G))
    if sym_name not in _SYMPY_NAME:
        raise PipelineError(f"unexpected Galois group label: {sym_name!r}")
    name = _SYMPY_NAME[sym_name]

    # consistency: SymPy's `alt` flag is A5-membership; cross-check it
    # against the discriminant invariant (square iff G <= A5)
    if bool(alt) != disc_sq:
        # the two invariants disagree — flag loudly rather than guess
        raise PipelineError(
            f"internal inconsistency: A5 flag={bool(alt)} but "
            f"disc_square={disc_sq} for {f.as_expr()}"
        )

    table = GROUP_TABLE[name]
    method = (
        "SymPy galois_group (quintic hybrid of Cohen Alg 6.3.9: sextic "
        "resolvent R51 coefficient lookup + discriminant squareness + "
        "quadratic resolvent R2; Tschirnhaus retries). Discriminant "
        f"{disc} ({'square' if disc_sq else 'not a square'})."
    )
    return GroupResult(
        name=name,
        order=table["order"],
        in_A5=table["in_A5"],
        solvable=table["solvable"],
        discriminant=disc,
        disc_square=disc_sq,
        method=method,
    )
