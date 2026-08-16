"""S1 — reduction to normal form (v1 document section 3).

Depressed quintic: the exact substitution x = y - a4/5 kills the x^4 term.
Palindromic reduction: the *correct* reduction of a reciprocal quintic,
which always has x = -1 as a root; the palindromic quartic then reduces
to a quadratic in t = x + 1/x. (The v1 document's loose "cubic in
x + 1/x" is superseded — see PalindromicReduction.note.)

Bring-Jerrard form (x^5 + p x + q) is intentionally NOT computed in v1:
Tschirnhaus reductions risk severe coefficient blow-up (plan risk #3) and
no downstream stage needs the form. The pipeline records a note instead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple, Union

import sympy as sp

__all__ = [
    "NormalFormResult",
    "PalindromicReduction",
    "BringJerrard",
    "depress_quintic",
]


@dataclass
class PalindromicReduction:
    """Closed-form reduction of a palindromic (reciprocal) quintic.

    A palindromic monic quintic f(x) = x^5 + a x^4 + b x^3 + b x^2 + a x + 1
    (coefficients satisfy a_i = a_{5-i}) always satisfies f(-1) = 0.
    Factoring out (x + 1) leaves the palindromic quartic
        Q(x) = x^4 + A x^3 + B x^2 + A x + 1,
    where A = a - 1 and B = b - a + 1.
    Dividing by x^2 and setting t = x + 1/x gives the *quadratic*
        t^2 + A t + (B - 2) = 0,
    whose two roots t1, t2 each yield a quadratic x^2 - t_i x + 1 = 0.
    (The v1 document's "cubic in x + 1/x" is a loose statement; the
    correct reduction is this quadratic — the quintic's fifth root is
    simply -1.)
    """

    root_from_minus_one: sp.Expr
    t_quadratic: sp.Poly          # in symbol t
    t_roots: Tuple[sp.Expr, sp.Expr]
    x_roots_from_t: Tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr]
    all_roots: Tuple[sp.Expr, ...]  # 5 exact radical expressions
    note: str


@dataclass
class BringJerrard:
    """Bring-Jerrard normal form x^5 + p x + q (unused in v1)."""

    p: sp.Rational
    q: sp.Rational
    transform: sp.Expr  # x = t + transform(t)


@dataclass
class NormalFormResult:
    depressed: sp.Poly
    shift: sp.Rational
    palindromic: bool
    palindromic_reduction: Optional[PalindromicReduction]
    bring_jerrard: Optional[BringJerrard]
    notes: Tuple[str, ...] = field(default=())


def _is_palindromic_monic(coeffs_desc) -> bool:
    """coeffs_desc = [a5, a4, a3, a2, a1, a0]; reciprocal iff a_i == a_{5-i}."""
    a5, a4, a3, a2, a1, a0 = coeffs_desc
    return a5 == a0 and a4 == a1 and a3 == a2


def _palindromic_reduction(f: sp.Poly) -> PalindromicReduction:
    """Build the closed-form palindromic reduction of a monic quintic.

    f must be x^5 + a x^4 + b x^3 + b x^2 + a x + 1 (reciprocal).
    """
    x = f.gen
    _, a, b, _b, _a, _one = f.all_coeffs()  # a = a4 = a1, b = a3 = a2

    # Q(x) = f(x) / (x + 1), palindromic quartic x^4 + A x^3 + B x^2 + A x + 1
    A = a - 1
    B = b - a + 1
    Q = sp.Poly(x**4 + A*x**3 + B*x**2 + A*x + 1, x, domain=sp.ZZ)

    # sanity: exact division must hold
    q, rem = sp.div(f.as_expr(), x + 1)
    assert rem == 0, "palindromic quintic must be divisible by (x+1)"
    assert sp.expand(sp.sympify(q)) == Q.as_expr(), "quartic reduction mismatch"

    # t-quadratic: t^2 + A t + (B - 2)
    t = sp.symbols("t")
    tquad = sp.Poly(t**2 + A*t + (B - 2), t, domain=sp.ZZ)
    t_roots = tuple(sp.roots(tquad, t).keys())
    assert len(t_roots) == 2, "t-quadratic must split over the radicals"

    # For each t_i: x^2 - t_i x + 1 = 0  =>  x = (t_i +- sqrt(t_i^2 - 4))/2
    x_roots = []
    for ti in t_roots:
        disc = ti**2 - 4
        x_roots.append((ti + sp.sqrt(disc)) / 2)
        x_roots.append((ti - sp.sqrt(disc)) / 2)
    x_roots = tuple(sp.simplify(r) for r in x_roots)

    note = (
        "Palindromic quintic reduced correctly: x = -1 is always a root; "
        "the remaining palindromic quartic reduces to a QUADRATIC in "
        "t = x + 1/x (t^2 + A t + (B - 2)), not the 'cubic in x + 1/x' "
        "stated loosely in QuinticMethods_v1.md section 5."
    )
    return PalindromicReduction(
        root_from_minus_one=sp.Integer(-1),
        t_quadratic=tquad,
        t_roots=t_roots,
        x_roots_from_t=x_roots,
        all_roots=(sp.Integer(-1),) + x_roots,
        note=note,
    )


def depress_quintic(f: sp.Poly) -> NormalFormResult:
    """Compute the normal form of a (monic or primitive) quintic.

    - Depressed form via x = y - a4/5 (exact rational arithmetic), computed
      from the monic form so the shift is clean.
    - Palindromic detection on the original monic coefficients, with the
      full closed-form reduction when present.
    - Bring-Jerrard: skipped in v1 (coefficient blow-up risk); a note is
      recorded instead.
    """
    f = sp.Poly(f, f.gen)
    if f.degree() != 5:
        raise ValueError("depress_quintic expects a quintic")

    # work from the monic form
    lc = f.LC()
    f_monic = sp.Poly(f.as_expr() / lc, f.gen, domain=sp.QQ)
    coeffs = [sp.Rational(c) for c in f_monic.all_coeffs()]
    a4 = coeffs[1]

    shift = -a4 / 5
    # depressed(y) = f_monic(y + shift)
    y = sp.symbols("y")
    dep_expr = sp.expand(f_monic.as_expr().subs(f.gen, y + shift))
    dep_coeffs = sp.Poly(dep_expr, y).all_coeffs()
    # drop the (numerically) zero x^4 coefficient exactly
    dep_coeffs = [c for c in dep_coeffs]
    assert dep_coeffs[1] == 0, "depression failed to kill the x^4 term"
    # return ZZ domain if all coefficients are integers, else QQ
    if all(c.is_integer for c in dep_coeffs):
        depressed = sp.Poly([int(c) for c in dep_coeffs], y, domain=sp.ZZ)
    else:
        depressed = sp.Poly(dep_coeffs, y, domain=sp.QQ)

    notes = [
        "Depressed quintic via x = y - a4/5 = y + "
        f"{shift} (exact rational substitution; the same first step inside "
        "SymPy's roots_quintic)."
    ]

    palindromic = _is_palindromic_monic(coeffs)
    palindromic_reduction = (
        _palindromic_reduction(f_monic) if palindromic else None
    )

    notes.append(
        "Bring-Jerrard reduction (x^5 + p x + q) skipped in v1: "
        "coefficient blow-up risk; see plan risk #3."
    )

    return NormalFormResult(
        depressed=depressed,
        shift=shift,
        palindromic=palindromic,
        palindromic_reduction=palindromic_reduction,
        bring_jerrard=None,
        notes=tuple(notes),
    )
