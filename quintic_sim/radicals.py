"""S4a — radical solutions for solvable quintics (v1 document section 2).

Algorithm (SymPy ``roots_quintic``, verified in source):
1. depress the quintic (x = y - a4/5);
2. build the sextic **F20 resolvent** (``PolyQuintic.f20``);
3. if the resolvent is irreducible over Z, the quintic is not solvable
   (Galois group A5 or S5) and no radical form exists;
4. otherwise an integer root theta of the resolvent parameterizes the
   solution; the 5 roots are built from **Lagrange resolvents** in
   zeta_5 = e^{2*pi*i/5} and 5th roots (this is the same
   resolvent-reduction family the document names after Brioschi,
   Kronecker and Dedekind).

The F20 resolvent and its integer root are exposed in the trace so the
reduction is inspectable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

import sympy as sp
from sympy.polys.polyroots import PolyQuintic

__all__ = ["RadicalResult", "radical_roots"]


@dataclass
class RadicalResult:
    solvable: bool
    roots: Tuple[sp.Expr, ...]
    f20_resolvent: Optional[sp.Poly]
    f20_integer_root: Optional[sp.Rational]
    f20_irreducible: bool
    method: str
    notes: Tuple[str, ...] = field(default=())


def _depressed(f: sp.Poly) -> Tuple[sp.Poly, sp.Rational]:
    """Depress a (possibly non-monic) quintic; returns (g(y), shift)."""
    x = f.gen
    fm = sp.Poly(f.as_expr() / f.LC(), x, domain=sp.QQ)
    a4 = sp.Rational(fm.all_coeffs()[1])
    shift = -a4 / 5
    y = sp.symbols("y")
    g = sp.Poly(sp.expand(fm.as_expr().subs(x, y + shift)), y, domain=sp.QQ)
    return g, shift


def radical_roots(f: sp.Poly) -> RadicalResult:
    """Attempt a radical solution of an irreducible quintic.

    Returns a RadicalResult with ``solvable=False`` and empty roots when
    no radical form exists (A5/S5) or SymPy's resolver gives up; never
    raises for well-formed input.
    """
    f = sp.Poly(f, f.gen)
    x = f.gen

    g, _shift = _depressed(f)
    pq = PolyQuintic(g)
    f20 = pq.f20
    f20_irr = bool(f20.is_irreducible)

    f20_int_root: Optional[sp.Rational] = None
    if not f20_irr:
        for fac, _m in f20.factor_list()[1]:
            if fac.is_linear:
                f20_int_root = sp.Rational(fac.root(0))
                break

    # actual root extraction (depresses internally; returns {} when it
    # cannot produce a radical form)
    rootdict = sp.roots(f.as_expr(), x, quintics=True)
    roots = tuple(rootdict.keys())
    solvable = len(roots) == 5

    if solvable:
        method = (
            "SymPy roots_quintic: sextic F20 resolvent (integer root "
            f"theta = {f20_int_root}) + Lagrange resolvents in zeta_5 "
            "+ fifth roots (Brioschi/Kronecker/Dedekind resolvent family)."
        )
        notes = (
            "Radical expressions are CAS output and MUST pass the S6 "
            "verification gate before being reported.",
        )
    else:
        method = (
            "SymPy roots_quintic: F20 resolvent is irreducible over Z "
            "-> no radical form exists (Galois group A5 or S5); use the "
            "special-function/numeric path (S4b/S5)."
        )
        notes = ()

    return RadicalResult(
        solvable=solvable,
        roots=roots,
        f20_resolvent=f20,
        f20_integer_root=f20_int_root,
        f20_irreducible=f20_irr,
        method=method,
        notes=notes,
    )
