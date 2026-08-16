"""Tests for S4b — special/exact forms — and S5 — numerical roots."""

import random

import mpmath
import numpy as np
import pytest
import sympy as sp

from quintic_sim.numeric import NumericResult, numeric_roots
from quintic_sim.special import SpecialResult, special_forms

x = sp.symbols("x")

A5 = [1, -2, -1, -3, 2, -3]
S5 = [1, 0, 0, -5, 5, 1]
F20 = [1, 0, 0, 0, 0, -2]  # x^5 - 2: has p, q in Bring-Jerrard form already


def _poly(coeffs):
    return sp.Poly(coeffs, x, domain=sp.ZZ)


def _aberth(coeffs, dps=40):
    with mpmath.workdps(dps):
        return mpmath.polyroots(coeffs, maxsteps=200, cleanup=True)


class TestSpecialForms:
    @pytest.mark.parametrize("coeffs", [A5, S5])
    def test_crootof_forms_for_all_five_roots(self, coeffs):
        r = special_forms(_poly(coeffs))
        assert r.crootofs is not None
        assert len(r.crootofs) == 5
        # each CRootOf evaluates to a root: matches Aberth as a multiset
        with mpmath.workdps(40):
            got = sorted(
                (float(mpmath.re(sp.N(c, 30))), float(mpmath.im(sp.N(c, 30))))
                for c in r.crootofs
            )
            exp = sorted(
                (float(mpmath.re(z)), float(mpmath.im(z))) for z in _aberth(coeffs)
            )
        for (gr, gi), (er, ei) in zip(got, exp):
            assert abs(gr - er) < 1e-15
            assert abs(gi - ei) < 1e-15

    def test_bring_radical_display(self):
        # x^5 - 2 is already Bring-Jerrard: p = 0, q = -2
        r = special_forms(_poly(F20))
        assert r.bring_radical is not None
        assert "Br" in r.bring_radical
        assert "p" in r.bring_radical and "q" in r.bring_radical

    def test_bring_radical_formula_numeric_check(self):
        # x^5 + 5x - 12 (S5, Bring-Jerrard with p != 0):
        # x = p^(1/4) * Br(-q * p^(-5/4)) must give the real root
        r = special_forms(_poly([1, 0, 0, 0, 5, -12]))
        assert r.bring_radical is not None
        with mpmath.workdps(40):
            z_mp = mpmath.mpf(sp.N(-sp.Rational(-12) * 5**sp.Rational(-5, 4), 40))
            br = mpmath.findroot(lambda t: t**5 + t - z_mp, 0.5)
            formula = mpmath.mpf(5) ** (mpmath.mpf(1) / 4) * br
            real = [z for z in _aberth([1, 0, 0, 0, 5, -12])
                    if abs(mpmath.im(z)) < 1e-30][0]
        assert abs(formula - real) < 1e-30

    def test_non_bring_jerrard_has_no_bring_display(self):
        # A5 vector is not in x^5 + px + q form
        r = special_forms(_poly(A5))
        assert r.bring_radical is None

    def test_klein_stub_present(self):
        r = special_forms(_poly(A5))
        assert r.klein is not None
        assert "icosahedral" in r.klein.lower()
        assert "TODO" in r.klein


class TestNumericRoots:
    @pytest.mark.parametrize("coeffs", [A5, S5, F20])
    def test_aberth_five_roots(self, coeffs):
        r = numeric_roots(_poly(coeffs), dps=50)
        assert len(r.aberth) == 5
        assert r.n_converged is True

    def test_numpy_companion_cross_check(self):
        r = numeric_roots(_poly(S5))
        assert r.numpy_match is True
        # agreement to ~1e-9
        with mpmath.workdps(30):
            a = sorted((float(mpmath.re(z)), float(mpmath.im(z))) for z in r.aberth)
        n = sorted((z.real, z.imag) for z in r.numpy_eigs)
        for (ar, ai), (nr, ni) in zip(a, n):
            assert abs(ar - nr) < 1e-8
            assert abs(ai - ni) < 1e-8

    def test_durand_kerner_converges(self):
        for coeffs in (A5, S5, F20):
            r = numeric_roots(_poly(coeffs))
            assert r.durand_iterations is not None
            assert r.durand_iterations > 0
            # Durand-Kerner roots must agree with Aberth (same multiset)
            with mpmath.workdps(30):
                a = sorted(
                    (float(mpmath.re(z)), float(mpmath.im(z))) for z in r.aberth
                )
            d = sorted((float(mpmath.re(z)), float(mpmath.im(z)))
                       for z in r.durand_roots)
            for (ar, ai), (dr, di) in zip(a, d):
                assert abs(ar - dr) < 1e-8
                assert abs(ai - di) < 1e-8

    def test_property_random_quintics_mpmath_vs_numpy(self):
        rng = random.Random(777)
        for _ in range(50):
            cs = [1] + [rng.randint(-6, 6) for _ in range(5)]
            f = _poly(cs)
            r = numeric_roots(f, dps=30)
            with mpmath.workdps(30):
                a = sorted(
                    (float(mpmath.re(z)), float(mpmath.im(z))) for z in r.aberth
                )
            n = sorted((z.real, z.imag) for z in r.numpy_eigs)
            for (ar, ai), (nr, ni) in zip(a, n):
                assert abs(ar - nr) < 1e-6
                assert abs(ai - ni) < 1e-6

    def test_real_classification(self):
        # x^5 - 2 has exactly one real root
        r = numeric_roots(_poly(F20))
        reals = [z for z in r.aberth if abs(mpmath.im(z)) < 1e-30]
        assert len(reals) == 1
