"""S4b — special / exact forms for unsolvable quintics (v1 document section 4).

- **CRootOf exact algebraic numbers** (primary): one per root, exact and
  evaluable to any precision. Real roots come from Vincent interval
  isolation (``sympy.real_roots``); all five are available by index via
  ``CRootOf(f, x, index=k)``.
- **Bring radical** (display-only, clearly labeled): when the quintic is
  (or can be read as) Bring-Jerrard form x^5 + p x + q, the real root is
  x = p^(1/4) * Br(-q * p^(-5/4)), where Br(z) is the generalized
  hypergeometric function solving t^5 + t - z = 0. No open-source CAS
  implements Br as a *callable*, so this is a NOTATION output, not a
  computation.
- **Klein icosahedral solution** (stub): documented recipe only —
  icosahedral invariants -> Schwarz triangle function (hypergeometric
  2F1). No open-source implementation exists; marked TODO(future).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

import sympy as sp
from sympy.polys.rootoftools import CRootOf

__all__ = ["SpecialResult", "special_forms"]


@dataclass
class SpecialResult:
    crootofs: Optional[Tuple[sp.Expr, ...]]   # 5 exact algebraic numbers
    bring_radical: Optional[str]              # notation, or None
    klein: Optional[str]                      # stub text
    notes: Tuple[str, ...] = field(default=())


def _is_bring_jerrard_monic(f: sp.Poly) -> Optional[Tuple[sp.Rational, sp.Rational]]:
    """Return (p, q) if f (monic) is x^5 + p x + q, else None."""
    coeffs = [sp.Rational(c) for c in f.all_coeffs()]
    if len(coeffs) == 6 and coeffs[1] == 0 and coeffs[2] == 0 and coeffs[3] == 0:
        return coeffs[4], coeffs[5]
    return None


def special_forms(f: sp.Poly) -> SpecialResult:
    """Build the exact/special-function forms for a (typically unsolvable)
    irreducible quintic."""
    f = sp.Poly(f, f.gen, domain=sp.ZZ)
    x = f.gen
    notes = []

    # --- CRootOf forms for all five roots ---
    crootofs = tuple(CRootOf(f.as_expr(), x, index=k) for k in range(5))
    notes.append(
        "CRootOf exact algebraic numbers (index 0..4; real roots via "
        "Vincent interval isolation) — honest 'closed form' objects, "
        "evaluable to any precision."
    )

    # --- Bring radical (notation only) ---
    bring = None
    bj = _is_bring_jerrard_monic(sp.Poly(f.as_expr(), x, domain=sp.QQ))
    if bj is not None:
        p, q = bj
        if p != 0:
            bring = (
                f"x = p^(1/4) * Br(-q * p^(-5/4)) with p = {p}, q = {q}; "
                "Br(z) is the Bring radical (generalized hypergeometric "
                "function solving t^5 + t - z = 0). NOTATION ONLY — no "
                "open-source CAS implements Br as a callable."
            )
        else:
            bring = (
                f"x^5 + q = 0 with q = {q}: already Bring-Jerrard with "
                "p = 0; the real root is x = (-q)^(1/5) (a radical), the "
                "complex ones via zeta_5. Bring radical Br is trivially "
                "unneeded here."
            )
    else:
        notes.append(
            "Not in Bring-Jerrard form x^5 + p x + q; a Tschirnhaus "
            "reduction would be needed (skipped in v1, plan risk #3)."
        )

    # --- Klein stub ---
    klein = (
        "Klein icosahedral solution (1888) — TODO(future), documented "
        "recipe only: reduce to the icosahedral equation via the three "
        "icosahedral invariants (J, H, T), then solve with the Schwarz "
        "triangle function (a hypergeometric 2F1). No open-source "
        "implementation exists; this is the standard modern answer to "
        "'how do you solve the general quintic' but is not computed here."
    )

    return SpecialResult(
        crootofs=crootofs,
        bring_radical=bring,
        klein=klein,
        notes=tuple(notes),
    )
