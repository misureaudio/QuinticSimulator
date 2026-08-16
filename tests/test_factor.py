"""Tests for S2 — factorization over Q (rational root test + Zassenhaus)."""

import sympy as sp

from quintic_sim.factor import factor_quintic, rational_root_test

x = sp.symbols("x")

C5 = [1, 1, -4, -3, 3, 1]
D5 = [1, -2, -3, 0, 0, -1]
F20 = [1, 0, 0, 0, 0, -2]
A5 = [1, -2, -1, -3, 2, -3]
S5 = [1, 0, 0, -5, 5, 1]
REDUCIBLE = [1, 1, 1, 1, 1, -5]      # (x-1)(x^4+2x^3+3x^2+4x+5)
RATIONAL_ROOT = [1, -6, 13, -12, 5, -1]  # (x-1)(x^4-5x^3+8x^2-4x+1)
MULTIPLE_ROOT = [1, 0, 0, 0, -5, 4]  # (x-1)^2 (x^3+2x^2+3x+4)
IRRREDUCIBLE_VECTORS = [C5, D5, F20, A5, S5]


def _poly(coeffs):
    return sp.Poly(coeffs, x, domain=sp.ZZ)


class TestRationalRootTest:
    def test_finds_root_one(self):
        assert rational_root_test(_poly(RATIONAL_ROOT)) == [sp.Rational(1)]

    def test_finds_root_minus_one(self):
        # x^5 + 2x^4 - 3x^3 - 3x^2 + 2x + 1 has roots -1 and 1
        assert rational_root_test(_poly([1, 2, -3, -3, 2, 1])) == [
            sp.Rational(-1),
            sp.Rational(1),
        ]

    def test_no_rational_roots(self):
        for coeffs in IRRREDUCIBLE_VECTORS:
            assert rational_root_test(_poly(coeffs)) == []

    def test_zero_constant_term_gives_zero_root(self):
        # x^5 - x^3 = x^3 (x^2 - 1): 0 is a rational root
        assert sp.Rational(0) in rational_root_test(_poly([1, 0, -1, 0, 0, 0]))


class TestFactorQuintic:
    def test_rational_root_vector(self):
        r = factor_quintic(_poly(RATIONAL_ROOT))
        assert r.rational_roots == (sp.Rational(1),)
        assert r.reducible is True
        degs = sorted(f.degree() for f, _ in r.factorization)
        assert degs == [1, 4]
        lin = [f for f, m in r.factorization if f.degree() == 1]
        assert sp.simplify(lin[0].as_expr() - (x - 1)) == 0

    def test_reducible_vector(self):
        r = factor_quintic(_poly(REDUCIBLE))
        assert r.rational_roots == (sp.Rational(1),)
        assert r.reducible is True
        degs = sorted(f.degree() for f, _ in r.factorization)
        assert degs == [1, 4]

    def test_multiple_root_multiplicity(self):
        r = factor_quintic(_poly(MULTIPLE_ROOT))
        assert r.rational_roots == (sp.Rational(1),)
        assert r.reducible is True
        lin = [m for f, m in r.factorization if f.degree() == 1]
        assert lin == [2]
        cubics = [f for f, m in r.factorization if f.degree() == 3]
        assert sp.simplify(
            cubics[0].as_expr() - (x**3 + 2*x**2 + 3*x + 4)
        ) == 0

    def test_irreducible_vectors_stay_whole(self):
        for coeffs in IRRREDUCIBLE_VECTORS:
            r = factor_quintic(_poly(coeffs))
            assert r.reducible is False
            assert r.rational_roots == ()
            assert len(r.factorization) == 1
            f, m = r.factorization[0]
            assert m == 1
            assert f.degree() == 5

    def test_factorization_reconstructs_polynomial(self):
        for coeffs in [RATIONAL_ROOT, REDUCIBLE, MULTIPLE_ROOT] + IRRREDUCIBLE_VECTORS:
            f = _poly(coeffs)
            r = factor_quintic(f)
            prod = sp.expand(sp.Mul(*[sp.Pow(fac.as_expr(), m) for fac, m in r.factorization]))
            assert prod == f.as_expr()

    def test_notes_name_zassenhaus(self):
        r = factor_quintic(_poly(RATIONAL_ROOT))
        assert any("zassenhaus" in n.lower() for n in r.notes)
