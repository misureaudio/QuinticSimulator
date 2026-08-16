"""Tests for S1 — normal form (depressed quintic, palindromic reduction)."""

import mpmath
import pytest
import sympy as sp

from quintic_sim.normalform import depress_quintic

x = sp.symbols("x")
y = sp.symbols("y")

C5 = [1, 1, -4, -3, 3, 1]
D5 = [1, -2, -3, 0, 0, -1]
F20 = [1, 0, 0, 0, 0, -2]
A5 = [1, -2, -1, -3, 2, -3]
S5 = [1, 0, 0, -5, 5, 1]
PALINDROMIC = [1, 2, -3, -3, 2, 1]  # (x-1)^2 (x+1) (x^2+3x+1)
GROUP_VECTORS = [C5, D5, F20, A5, S5]


def _poly(coeffs):
    return sp.Poly(coeffs, x, domain=sp.ZZ)


class TestDepressedForm:
    @pytest.mark.parametrize("coeffs", GROUP_VECTORS)
    def test_x4_term_killed(self, coeffs):
        r = depress_quintic(_poly(coeffs))
        assert r.depressed.degree() == 5
        assert r.depressed.all_coeffs()[1] == 0

    @pytest.mark.parametrize("coeffs", GROUP_VECTORS)
    def test_shift_is_minus_a4_over_5(self, coeffs):
        f = _poly(coeffs)
        r = depress_quintic(f)
        a4 = sp.Rational(f.all_coeffs()[1], 1)
        assert r.shift == -a4 / 5

    @pytest.mark.parametrize("coeffs", GROUP_VECTORS)
    def test_depressed_equals_shifted_original(self, coeffs):
        f = _poly(coeffs)
        r = depress_quintic(f)
        lhs = sp.expand(f.as_expr().subs(x, y + r.shift))
        rhs = sp.expand(r.depressed.as_expr())
        assert sp.simplify(lhs - rhs) == 0

    def test_shifted_roots_map_back(self):
        # roots of depressed g(y) satisfy g(yi) = 0  <=>  f(yi + shift) = 0
        f = _poly(C5)
        r = depress_quintic(f)
        with mpmath.workdps(30):
            # exact mpf rationals (no float64 degradation)
            coeffs = [mpmath.mpf(sp.Rational(c)) for c in r.depressed.all_coeffs()]
            roots_y = mpmath.polyroots(coeffs, maxsteps=200)
            f_expr = sp.lambdify(x, f.as_expr(), "mpmath")
            for ry in roots_y:
                val = f_expr(ry + mpmath.mpf(r.shift))
                assert abs(val) < 1e-18


class TestPalindromicDetection:
    def test_palindromic_flag_true(self):
        r = depress_quintic(_poly(PALINDROMIC))
        assert r.palindromic is True
        assert r.palindromic_reduction is not None

    @pytest.mark.parametrize("coeffs", GROUP_VECTORS)
    def test_non_palindromic_flag_false(self, coeffs):
        r = depress_quintic(_poly(coeffs))
        assert r.palindromic is False
        assert r.palindromic_reduction is None


def _reduction():
    return depress_quintic(_poly(PALINDROMIC)).palindromic_reduction


class TestPalindromicReduction:
    def test_minus_one_is_root(self):
        reduction = _reduction()
        assert sp.simplify(reduction.root_from_minus_one) == -1

    def test_t_quadratic_is_quadratic(self):
        reduction = _reduction()
        assert reduction.t_quadratic.degree() == 2

    def test_t_quadratic_expected(self):
        reduction = _reduction()
        # x^5 + 2x^4 - 3x^3 - 3x^2 + 2x + 1: a=2, b=-3
        # t-quadratic: t^2 + (a-1) t + (b-a-1) = t^2 + t - 6
        t = reduction.t_quadratic.gen
        expected = sp.Poly(t**2 + t - 6, t)
        assert sp.expand(
            reduction.t_quadratic.as_expr() - expected.as_expr()
        ) == 0

    def test_all_roots_match_numeric(self):
        reduction = _reduction()
        with mpmath.workdps(30):
            expected = mpmath.polyroots(PALINDROMIC, maxsteps=200)
            got = [mpmath.mpc(complex(sp.N(rt, 30))) for rt in reduction.all_roots]
        key = lambda z: (float(mpmath.re(z)), float(mpmath.im(z)))
        expected.sort(key=key)
        got.sort(key=key)
        assert len(got) == 5
        for ge, gg in zip(expected, got):
            # 1e-15: float64 conversion in the mpc(complex(...)) step
            assert abs(ge - gg) < 1e-15

    def test_note_mentions_cubic_correction(self):
        reduction = _reduction()
        assert "cubic" in reduction.note.lower()


class TestBringJerrardPolicy:
    @pytest.mark.parametrize("coeffs", GROUP_VECTORS + [PALINDROMIC])
    def test_bring_jerrard_skipped_with_note(self, coeffs):
        r = depress_quintic(_poly(coeffs))
        assert r.bring_jerrard is None
        assert any("bring" in n.lower() for n in r.notes)
