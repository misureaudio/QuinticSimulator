"""S0 — input parsing, normalization, squarefree decomposition.

Accepts a list of rational coefficients (descending order) or a SymPy
expression in one symbol. Normalizes to a primitive integer polynomial
(roots unchanged) and records the monic rational form. Computes the
squarefree decomposition via gcd with the derivative.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Sequence, Tuple, Union

import sympy as sp

from .errors import PipelineError

__all__ = ["ParsedInput", "parse_input"]

# A coefficient can be int, float, Fraction, sympy.Rational, or sympy Expr.
_Coef = Union[int, float, Fraction, sp.Expr]


@dataclass
class ParsedInput:
    """Result of S0 normalization.

    poly          -- primitive integer (ZZ) polynomial, leading coeff may be >1
    monic         -- monic rational (QQ) form, same roots
    squarefree    -- True if gcd(f, f') == 1
    sqf_factors   -- tuple of (factor, multiplicity) from squarefree decomp
    warnings      -- tuple of human-readable warning strings
    """

    poly: sp.Poly
    monic: sp.Poly
    squarefree: bool
    sqf_factors: Tuple[Tuple[sp.Poly, int], ...] = field(default=())
    warnings: Tuple[str, ...] = ()


def _to_rational(c: _Coef, where: str) -> sp.Rational:
    """Convert a coefficient to sympy.Rational, rejecting non-rational input."""
    if isinstance(c, sp.Expr):
        # Reject any expression containing non-rational symbols/constants.
        if c.free_symbols:
            raise PipelineError(
                f"non-rational coefficient in {where}: {c} contains symbols"
            )
        # Check for irrational constants (pi, sqrt of non-square, E, etc.)
        if not c.is_rational and not c.is_zero:
            raise PipelineError(
                f"non-rational coefficient in {where}: {c} is not rational"
            )
        return sp.Rational(c)
    if isinstance(c, float):
        # Only accept floats that are exactly representable as rationals
        # with small denominators; otherwise treat as non-rational.
        frac = sp.Rational(c).limit_denominator(10**12)
        if abs(float(frac) - c) > 1e-12:
            raise PipelineError(
                f"non-rational coefficient in {where}: {c!r} is not rational"
            )
        return frac
    # int / Fraction / sympy.Rational
    try:
        return sp.Rational(c)
    except Exception as e:  # noqa: BLE001
        raise PipelineError(f"non-rational coefficient in {where}: {c!r}") from e


def _coerce_expr_to_list(expr: sp.Expr) -> Tuple[List[_Coef], sp.Symbol]:
    """Turn a single-variable SymPy expression into a descending coeff list."""
    if not expr.free_symbols:
        raise PipelineError("expression has no variable (not a polynomial)")
    if len(expr.free_symbols) > 1:
        sym = next(iter(expr.free_symbols))
        raise PipelineError(
            f"expression must be in exactly one variable, got "
            f"{len(expr.free_symbols)} symbols (e.g. {sym})"
        )
    sym = next(iter(expr.free_symbols))
    poly = sp.Poly(expr, sym)
    # as_expr_list gives ascending; we want descending.
    coeffs_asc = poly.all_coeffs()
    # all_coeffs already returns descending [a_n, ..., a_0].
    return list(coeffs_asc), sym


def parse_input(
    coeffs: Union[Sequence[_Coef], sp.Expr],
    *,
    symbol: sp.Symbol | str | None = None,
) -> ParsedInput:
    """Parse and normalize a quintic polynomial.

    Parameters
    ----------
    coeffs :
        Either a sequence of rational coefficients in *descending* order
        [a_5, a_4, ..., a_0], or a SymPy expression in a single variable.
    symbol :
        The symbol name if ``coeffs`` is an expression (auto-detected if
        omitted).

    Returns
    -------
    ParsedInput with the primitive integer polynomial, monic rational form,
    squarefree flag, and squarefree factors.

    Raises
    ------
    PipelineError
        If the input is not a degree-5 polynomial with rational coefficients.
    """
    warnings: List[str] = []

    # ---- accept either an expression, a string, or a coefficient list ----
    if isinstance(coeffs, str):
        coeffs = sp.sympify(coeffs)
    if isinstance(coeffs, sp.Expr):
        coeff_list, sym = _coerce_expr_to_list(coeffs)
    else:
        if symbol is None:
            symbol = "x"
        sym = sp.Symbol(symbol)
        if isinstance(coeffs, (str, bytes)) or (
            hasattr(coeffs, "__len__") and len(coeffs) == 0
        ):
            raise PipelineError("empty coefficient input")
        coeff_list = list(coeffs)

    if len(coeff_list) == 0:
        raise PipelineError("empty coefficient input")

    # ---- convert coefficients to rational ----
    rationals: List[sp.Rational] = []
    for i, c in enumerate(coeff_list):
        rationals.append(_to_rational(c, f"coefficient a_{len(coeff_list)-1-i}"))

    # ---- strip leading zeros ----
    while rationals and rationals[0] == 0:
        rationals = rationals[1:]
        warnings.append("stripped leading zero coefficient(s)")

    if not rationals:
        raise PipelineError("zero polynomial is not a quintic")

    # ---- build the polynomial ----
    poly = sp.Poly(rationals, sym)
    deg = poly.degree()
    if deg != 5:
        raise PipelineError(
            f"expected degree 5 (quintic), got degree {deg}"
        )

    # ---- monic rational form ----
    lc = poly.LC()
    monic = sp.Poly(poly.as_expr() / lc, sym, domain=sp.QQ)

    # ---- primitive integer form (clear denominators, divide by content) ----
    # Multiply through by lcm of denominators to get integer coefficients,
    # then divide by the gcd (content) of all coefficients.
    nums = [sp.Rational(c) for c in poly.all_coeffs()]
    denom_lcm = 1
    for n in nums:
        denom_lcm = sp.lcm(denom_lcm, sp.denom(n))
    int_coeffs = [int(n * denom_lcm) for n in nums]
    content = 0
    for c in int_coeffs:
        content = sp.gcd(content, c)
    if content == 0:
        raise PipelineError("zero polynomial is not a quintic")
    int_coeffs = [c // content for c in int_coeffs]
    prim_poly = sp.Poly(int_coeffs, sym, domain=sp.ZZ)

    # ---- squarefree decomposition ----
    sqf = prim_poly.sqf_list()  # (content, [(factor, mult), ...])
    sqf_factors = tuple(sqf[1])
    squarefree = len(sqf_factors) == 1 and sqf_factors[0][1] == 1
    if not squarefree:
        mults = [m for _, m in sqf_factors if m > 1]
        warnings.append(
            f"polynomial has multiple roots (multiplicities {mults}); "
            "Galois-group analysis proceeds on the squarefree part"
        )

    return ParsedInput(
        poly=prim_poly,
        monic=monic,
        squarefree=squarefree,
        sqf_factors=sqf_factors,
        warnings=tuple(warnings),
    )
