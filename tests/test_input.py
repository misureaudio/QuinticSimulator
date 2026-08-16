"""Tests for S0 — input parsing, normalization, squarefree decomposition."""

import pytest

import sympy as sp

from quintic_sim.errors import PipelineError
from quintic_sim.input import parse_input

x = sp.symbols("x")

# ---- the verified test vectors (from the architecture plan, section 1) ----
C5 = [1, 1, -4, -3, 3, 1]          # x^5 + x^4 - 4x^3 - 3x^2 + 3x + 1
D5 = [1, -2, -3, 0, 0, -1]         # x^5 - 2x^4 - 3x^3 - 1
F20 = [1, 0, 0, 0, 0, -2]          # x^5 - 2
A5 = [1, -2, -1, -3, 2, -3]        # x^5 - 2x^4 - x^3 - 3x^2 + 2x - 3
S5 = [1, 0, 0, -5, 5, 1]           # x^5 - 5x^2 + 5x + 1
REDUCIBLE = [1, 1, 1, 1, 1, -5]    # (x-1)(x^4+2x^3+3x^2+4x+5)
PALINDROMIC = [1, 2, -3, -3, 2, 1] # x^5 + 2x^4 - 3x^3 - 3x^2 + 2x + 1
RATIONAL_ROOT = [1, -6, 13, -12, 5, -1]  # (x-1)(x^4-5x^3+8x^2-4x+1)
MULTIPLE_ROOT = [1, 0, 0, 0, -5, 4]      # (x-1)^2 (x^3 + 2x^2 + 3x + 4)


class TestParseAccepts:
    def test_all_five_group_vectors_parse(self):
        for coeffs in (C5, D5, F20, A5, S5):
            r = parse_input(coeffs)
            assert r.poly.degree() == 5
            assert r.squarefree
            assert r.warnings == ()

    def test_reducible_and_special_vectors_parse(self):
        for coeffs in (REDUCIBLE, PALINDROMIC, RATIONAL_ROOT):
            r = parse_input(coeffs)
            assert r.poly.degree() == 5

    def test_list_and_expr_inputs_agree(self):
        r1 = parse_input(C5)
        r2 = parse_input(x**5 + x**4 - 4*x**3 - 3*x**2 + 3*x + 1)
        assert r1.poly.as_expr() == r2.poly.as_expr()

    def test_leading_zeros_stripped(self):
        r = parse_input([0, 1, 0, 0, 0, 0, -2])  # leading 0, still x^5 - 2
        assert r.poly.as_expr() == x**5 - 2

    def test_string_expression_input(self):
        r = parse_input("x^5 - 2*x^4 - 3*x^3 - 1")
        assert r.poly.as_expr() == x**5 - 2*x**4 - 3*x**3 - 1

    def test_string_coeff_list_input(self):
        r = parse_input("1, 0, 0, 0, 0, -2")
        assert r.poly.as_expr() == x**5 - 2


class TestNormalization:
    def test_nonmonic_integer_input_becomes_monic(self):
        r = parse_input([2, 0, 0, 0, 0, -4])  # 2 x^5 - 4
        assert r.poly.as_expr() == x**5 - 2

    def test_fractional_coefficients_become_primitive_integer(self):
        r = parse_input([sp.Rational(1, 2), 0, 0, 0, sp.Rational(1, 3), 0])
        # monic x^5 + (2/3) x -> primitive integer form 3 x^5 + 2 x (same roots)
        assert r.poly.as_expr() == 3*x**5 + 2*x
        # and the recorded monic form is the rational one
        assert r.monic.as_expr() == x**5 + sp.Rational(2, 3)*x

    def test_output_is_always_integer_domain(self):
        for coeffs in (C5, D5, F20, A5, S5, [sp.Rational(1, 2), 0, 0, 0, 0, 1]):
            r = parse_input(coeffs)
            assert str(r.poly.domain) == "ZZ"

    def test_content_is_one(self):
        from functools import reduce
        from math import gcd
        for coeffs in (C5, D5, F20, A5, S5, [2, 0, 0, 0, 0, -4]):
            r = parse_input(coeffs)
            g = reduce(gcd, [abs(int(c)) for c in r.poly.all_coeffs()])
            assert g == 1


class TestSquarefree:
    def test_multiple_root_detected(self):
        r = parse_input(MULTIPLE_ROOT)
        assert not r.squarefree
        # (x-1)^2 times irreducible cubic
        factors = {f.as_expr(): m for f, m in r.sqf_factors}
        assert factors == {
            (x - 1): 2,
            (x**3 + 2*x**2 + 3*x + 4): 1,
        }
        assert any("multiple" in w.lower() or "repeated" in w.lower()
                   for w in r.warnings)

    def test_squarefree_vectors_flagged(self):
        # PALINDROMIC is excluded: it factors as (x-1)^2 (x+1)(x^2+3x+1)
        for coeffs in (C5, D5, F20, A5, S5, REDUCIBLE, RATIONAL_ROOT):
            r = parse_input(coeffs)
            assert r.squarefree
            # sqf decomposition of a squarefree poly is the poly itself to the 1st power
            assert len(r.sqf_factors) == 1
            assert r.sqf_factors[0][0].as_expr() == r.poly.as_expr()
            assert r.sqf_factors[0][1] == 1


class TestRejections:
    def test_rejects_quartic(self):
        with pytest.raises(PipelineError, match="[Dd]egree"):
            parse_input([1, 0, 0, 0, 0])

    def test_rejects_sextic(self):
        with pytest.raises(PipelineError, match="[Dd]egree"):
            parse_input([1, 0, 0, 0, 0, 0, 1])

    def test_rejects_zero_polynomial(self):
        with pytest.raises(PipelineError):
            parse_input([0, 0, 0, 0, 0, 0])

    def test_rejects_nonrational_coefficient(self):
        with pytest.raises(PipelineError, match="[Rr]ational"):
            parse_input([1, sp.pi, 0, 0, 0, 0])

    def test_rejects_empty_input(self):
        with pytest.raises(PipelineError):
            parse_input([])
