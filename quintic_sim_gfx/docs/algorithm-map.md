# Algorithm Map — theory ↔ implementation

Maps each hand-waved step in `QuinticMethods_v1.md` to the concrete
algorithm the simulator actually runs, plus the pitfalls discovered and
verified during the build (2026-08-15, on this machine).

## Stage map

| Stage | Module | Concrete algorithm | Notes / pitfalls |
|---|---|---|---|
| S0 input | `input.py` | exact rational normalization; squarefree split via `gcd(f, f')` (`Poly.sqf_list`) | rejects degree ≠ 5 and non-rational coefficients |
| S1 normal form | `normalform.py` | exact substitution `x = y − a₄/5`; palindromic detection + reduction | Bring-Jerrard **skipped** (coefficient blow-up, plan risk #3); see palindromic correction below |
| S2 factor | `factor.py` | Rational Root Theorem by exact divisor enumeration, then **Zassenhaus** (SymPy `factor_list`: GF(p) factor + Hensel lift + Mignotte-bound reconstruction) | **No LLL in SymPy's path** (verified: zero LLL references in `sympy/polys/factortools.py`). LLL-based reconstruction is PARI's approach, reachable only via the Sage cross-check |
| S3 Galois group | `galois.py` | SymPy `galois_group(f, by_name=True)` = `_galois_group_degree_5_hybrid`: **Cohen Alg 6.3.9** — sextic resolvent R₅₁ (coefficient lookup) + discriminant squareness + quadratic resolvent R₂, Tschirnhaus retries | **No LLL, no Stauduhar** at degree 5: identification degenerates to a 5-row table (order + A₅-membership). Stauduhar is PARI/Sage's higher-degree machinery. SymPy calls F₂₀ "M20". Raises on reducible input — S2 must run first |
| S3 cross-check | `sage_bridge.py` | Sage-in-Docker `f.galois_group()` (Cohen resolvent + table lookup internally) | verified Docker protocol below; transitive group number N = 1…5 → C5/D5/F20/A5/S5 |
| S4a radicals | `radicals.py` | SymPy `roots_quintic`: depress → **sextic F₂₀ resolvent** → integer root θ → **Lagrange resolvents in ζ₅** → fifth roots (the Brioschi/Kronecker/Dedekind resolvent family) | F₂₀ resolvent + θ exposed in the trace; returns `{}` for A₅/S₅ |
| S4b special | `special.py` | `CRootOf` exact algebraic numbers (Vincent interval isolation via `real_roots`) | Bring radical = **notation only** (formula `x = p^(1/4)·Br(−q·p^(−5/4))` verified numerically); Klein = documented stub (TODO future) |
| S5 numerics | `numeric.py` | mpmath `polyroots` (**Aberth**, 50 digits) + NumPy companion-matrix `eigvals` + Durand-Kerner (roots-of-unity seeding, convergence history) | **coefficient-ordering trap**: mpmath wants descending, NumPy `polycompanion` wants ascending — one adapter. Aberth does **not** converge on multiple roots → NumPy fallback (machine precision) |
| S6 gate | `verify.py` | 40-digit residual `|f(r)| < 1e-30·scale` + cross-match vs numerics (1e-25 for Aberth reference, 1e-6 for the NumPy fallback) | CAS radical output is treated as a **hypothesis**; failed roots are replaced by CRootOf forms + warning |
| S7 report | `report.py`, `pipeline.py`, `cli.py` | `Report` dataclass → Markdown + JSON (stable schema), `StepTrace` records with wall times | CLI: `python -m quintic_sim "…" [--verbose] [--sage] [--json out]` |

## Verified pitfalls (all hit and fixed during the build)

1. **Palindromic correction (document discrepancy, V10).**
   A palindromic monic quintic x⁵ + a x⁴ + b x³ + b x² + a x + 1
   always has x = −1 as a root. The remaining palindromic quartic
   reduces to a **quadratic** in t = x + 1/x:
   t² + (a−1)·t + (b−a−1) = 0, then two quadratics x² − tᵢ x + 1.
   `QuinticMethods_v1.md` §5's "cubic in x + 1/x" is a loose textbook
   statement; the simulator implements the correct version and prints
   the correction in the report.
2. **NumPy coefficient ordering (V6).** `np.polynomial.polynomial.polycompanion`
   wants **ascending** coefficients; `mpmath.polyroots` wants
   **descending**. Mixing them up silently solves the reciprocal
   polynomial.
3. **`cypari2` does not build on this Windows host** (no PARI C library)
   — PARI access goes through the Sage container only, and only as an
   optional cross-check.
4. **Sage image entrypoint quirk (V7).** The `sagemath/sagemath` image's
   default entrypoint swallows file-argument invocations. The verified
   working protocol is:

   ```bash
   docker run --rm --entrypoint /bin/bash sagemath/sagemath:latest -c \
     'sage << "SAGEEOF"
   <sage script that prints JSON>
   SAGEEOF'
   ```
5. **Aberth on multiple roots.** mpmath `polyroots` raises
   `NoConvergence` (even at maxsteps=2000) on polynomials with repeated
   roots (e.g. the palindromic test vector, double root at x=1). The
   NumPy companion matrix handles them; the gate's cross-match tolerance
   adapts (1e-6 instead of 1e-25) when the numeric reference is the
   machine-precision fallback.
6. **SymPy `galois_group` return shape.** `by_name=True` returns
   `(S5TransitiveSubgroups.<C5|D5|M20|A5|S5>, in_A5_flag)` — an *enum*,
   so order/solvability come from the classification table, and the
   `in_A5` flag is cross-checked against the discriminant invariant.
7. **float64 degradation in tests.** Comparing 50-digit mpmath roots
   through `complex()` loses precision (~1e-16); tests compare via
   `mpmath.mpf`/`mpc` or use tolerances that account for the conversion.

## Invariants tested

- `disc(f)` is a square in ℚ **iff** G ⊆ A₅ — checked on the 5 group
  vectors **and** 200 random irreducible quintics (property test).
- mpmath Aberth vs NumPy companion agree to 1e-6 on 50 random quintics.
- Factorization product reconstructs the input exactly.
- Palindromic reduction's 5 closed-form roots match Aberth numerically.
- Bring-radical formula p^(1/4)·Br(−q·p^(−5/4)) reproduces the real
  root of x⁵ + 5x − 12 to 1e-30.
- Sage and SymPy agree on all 5 group vectors (real Docker run).
