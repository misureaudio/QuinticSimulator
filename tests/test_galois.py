"""Tests for S3 — Galois-group computation and classification."""

import random

import pytest
import sympy as sp

from quintic_sim.errors import PipelineError
from quintic_sim.galois import GROUP_TABLE, classify

x = sp.symbols("x")

# (coeffs, expected canonical name, expected disc, expected disc-square)
VECTORS = {
    "C5": ([1, 1, -4, -3, 3, 1], "C5", 14641, True),
    "D5": ([1, -2, -3, 0, 0, -1], "D5", 55225, True),
    "F20": ([1, 0, 0, 0, 0, -2], "F20", 50000, False),
    "A5": ([1, -2, -1, -3, 2, -3], "A5", 2256004, True),
    "S5": ([1, 0, 0, -5, 5, 1], "S5", 1325000, False),
}


def _poly(coeffs):
    return sp.Poly(coeffs, x, domain=sp.ZZ)


class TestClassification:
    @pytest.mark.parametrize(
        "coeffs,name,disc,disc_sq",
        [(v[0], v[1], v[2], v[3]) for v in VECTORS.values()],
        ids=list(VECTORS),
    )
    def test_classifies_each_group(self, coeffs, name, disc, disc_sq):
        r = classify(_poly(coeffs))
        assert r.name == name
        assert r.discriminant == disc
        assert r.disc_square == disc_sq
        # table consistency
        assert r.order == GROUP_TABLE[name]["order"]
        assert r.in_A5 == GROUP_TABLE[name]["in_A5"]
        assert r.solvable == GROUP_TABLE[name]["solvable"]

    def test_solvable_are_exactly_c5_d5_f20(self):
        for name in ("C5", "D5", "F20"):
            assert GROUP_TABLE[name]["solvable"] is True
        for name in ("A5", "S5"):
            assert GROUP_TABLE[name]["solvable"] is False

    def test_orders(self):
        assert [GROUP_TABLE[n]["order"] for n in ("C5", "D5", "F20", "A5", "S5")] == [
            5, 10, 20, 60, 120,
        ]

    def test_in_A5_membership(self):
        assert [GROUP_TABLE[n]["in_A5"] for n in ("C5", "D5", "F20", "A5", "S5")] == [
            True, True, False, True, False,
        ]

    def test_method_names_the_algorithm(self):
        r = classify(_poly(VECTORS["S5"][0]))
        assert "resolvent" in r.method.lower() or "cohen" in r.method.lower()


class TestInvariants:
    def test_disc_square_iff_in_A5(self):
        """For every transitive quintic group, disc is a square iff G <= A5."""
        for coeffs, name, _d, _sq in VECTORS.values():
            r = classify(_poly(coeffs))
            assert r.disc_square == r.in_A5

    def test_random_irreducible_invariant(self):
        """Property test: 200 random irreducible quintics, disc_square == in_A5."""
        rng = random.Random(20260815)
        from math import isqrt

        checked = 0
        trials = 0
        while checked < 200 and trials < 4000:
            trials += 1
            cs = [1] + [rng.randint(-12, 12) for _ in range(5)]
            f = sp.Poly(cs, x, domain=sp.ZZ)
            if not f.is_irreducible:
                continue
            r = classify(f)
            d = r.discriminant
            # exact squareness (negative numbers are never squares in Q)
            root = isqrt(d) if d >= 0 else -1
            assert (root * root == d) == r.in_A5, (
                f"disc-square/A5 mismatch for {cs}: group={r.name}"
            )
            checked += 1
        assert checked == 200


class TestFailureModes:
    def test_reducible_input_raises_pipeline_error(self):
        f = _poly([1, 1, 1, 1, 1, -5])  # (x-1)(quartic)
        with pytest.raises(PipelineError) as ei:
            classify(f)
        assert "irreducible" in str(ei.value).lower()

    def test_degree_4_raises_pipeline_error(self):
        f = sp.Poly([1, 0, 0, 0, 0], x, domain=sp.ZZ)
        with pytest.raises(PipelineError):
            classify(f)
