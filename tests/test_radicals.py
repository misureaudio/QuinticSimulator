"""Tests for S4a — radical solutions — and S6 — the verification gate."""

import mpmath
import pytest
import sympy as sp

from quintic_sim.radicals import RadicalResult, radical_roots
from quintic_sim.verify import GateVerdict, VerificationGate

x = sp.symbols("x")

C5 = [1, 1, -4, -3, 3, 1]
D5 = [1, -2, -3, 0, 0, -1]
F20 = [1, 0, 0, 0, 0, -2]
A5 = [1, -2, -1, -3, 2, -3]
S5 = [1, 0, 0, -5, 5, 1]
SOLVABLE = {"C5": C5, "D5": D5, "F20": F20}
UNSOLVABLE = {"A5": A5, "S5": S5}


def _poly(coeffs):
    return sp.Poly(coeffs, x, domain=sp.ZZ)


def _aberth(coeffs, dps=40):
    with mpmath.workdps(dps):
        return mpmath.polyroots(coeffs, maxsteps=200, cleanup=True)


class TestRadicalRoots:
    @pytest.mark.parametrize("name,coeffs", list(SOLVABLE.items()))
    def test_solvable_vectors_give_five_radical_roots(self, name, coeffs):
        r = radical_roots(_poly(coeffs))
        assert r is not None
        assert r.solvable is True
        assert len(r.roots) == 5
        assert all(isinstance(rt, sp.Expr) for rt in r.roots)
        # the F20 resolvent trace
        assert r.f20_resolvent is not None
        assert r.f20_resolvent.degree() == 6
        assert not r.f20_irreducible

    @pytest.mark.parametrize("name,coeffs", list(UNSOLVABLE.items()))
    def test_unsolvable_vectors_give_none(self, name, coeffs):
        r = radical_roots(_poly(coeffs))
        assert r is not None
        assert r.solvable is False
        assert r.roots == ()
        # f20 resolvent of an A5/S5 quintic is irreducible over Z
        assert r.f20_resolvent is not None
        assert r.f20_irreducible is True

    def test_f20_resolvent_has_integer_root_for_solvable(self):
        for coeffs in SOLVABLE.values():
            r = radical_roots(_poly(coeffs))
            assert r.f20_integer_root is not None
            # exact check: the resolvent vanishes at theta
            assert r.f20_resolvent.as_expr().subs(
                r.f20_resolvent.gen, r.f20_integer_root
            ) == 0

    def test_method_names_the_algorithm(self):
        r = radical_roots(_poly(C5))
        assert "resolvent" in r.method.lower()


class TestVerifyRoot:
    def test_correct_radical_root_passes(self):
        f = _poly(F20)
        r = radical_roots(f)
        for rt in r.roots:
            v = GateVerdict.check_root(f, rt)
            assert v.ok, v.detail

    def test_wrong_root_fails_residual(self):
        f = _poly(F20)
        v = GateVerdict.check_root(f, sp.Rational(2))  # not a root of x^5-2
        assert v.ok is False
        assert "residual" in v.detail.lower()


class TestVerificationGate:
    @pytest.mark.parametrize("name,coeffs", list(SOLVABLE.items()))
    def test_radical_roots_pass_gate(self, name, coeffs):
        f = _poly(coeffs)
        r = radical_roots(f)
        numeric = _aberth(coeffs)
        gate = VerificationGate()
        verdicts = gate.run(f, list(r.roots), numeric)
        assert len(verdicts) == 5
        for v in verdicts:
            assert v.ok, f"{name}: {v.detail}"

    def test_crootof_roots_pass_gate(self):
        # the gate must also work for CRootOf exact forms (S4b)
        f = _poly(S5)
        from sympy.polys.rootoftools import CRootOf
        exact = [CRootOf(f.as_expr(), x, index=k) for k in range(5)]
        numeric = _aberth(S5)
        verdicts = VerificationGate().run(f, exact, numeric)
        assert all(v.ok for v in verdicts)

    def test_bad_root_is_flagged_not_silent(self):
        f = _poly(F20)
        r = radical_roots(f)
        good = list(r.roots)
        bad = good[:-1] + [sp.Rational(7)]  # 7 is not a root
        numeric = _aberth(F20)
        verdicts = VerificationGate().run(f, bad, numeric)
        assert any(not v.ok for v in verdicts)
