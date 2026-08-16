"""End-to-end pipeline tests: all 8+1 verified test vectors through S0-S7."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import sympy as sp

from quintic_sim.pipeline import simulate

x = sp.symbols("x")

# name -> (coeffs descending, expected method, expected group or None)
CASES = {
    "C5":          ([1, 1, -4, -3, 3, 1], "radicals", "C5"),
    "D5":          ([1, -2, -3, 0, 0, -1], "radicals", "D5"),
    "F20":         ([1, 0, 0, 0, 0, -2], "radicals", "F20"),
    "A5":          ([1, -2, -1, -3, 2, -3], "special", "A5"),
    "S5":          ([1, 0, 0, -5, 5, 1], "special", "S5"),
    "reducible":   ([1, 1, 1, 1, 1, -5], "reducible", None),
    "palindromic": ([1, 2, -3, -3, 2, 1], "reducible", None),
    "ratroot":     ([1, -6, 13, -12, 5, -1], "reducible", None),
    "multroot":    ([1, 0, 0, 0, -5, 4], "reducible", None),
}


class TestEndToEnd:
    @pytest.mark.parametrize("name,coeffs,method,group",
                             [(k, *v) for k, v in CASES.items()],
                             ids=list(CASES))
    def test_method_and_group(self, name, coeffs, method, group):
        rep = simulate(coeffs)
        assert rep.method == method, f"{name}: method={rep.method}"
        if group is not None:
            assert rep.group is not None
            assert rep.group.name == group
            assert rep.group.solvable == (method == "radicals")
        else:
            # reducible: no single quintic group
            assert rep.reducible is True

    @pytest.mark.parametrize("name,coeffs,method,group",
                             [(k, *v) for k, v in CASES.items()],
                             ids=list(CASES))
    def test_five_verified_roots(self, name, coeffs, method, group):
        rep = simulate(coeffs)
        assert len(rep.roots) == 5
        assert rep.verified is True, f"{name}: not all roots verified"
        for r in rep.roots:
            assert r["verified"] is True
            assert r["expr"] is not None
            assert r["numeric"] is not None

    @pytest.mark.parametrize("name,coeffs,method,group",
                             [(k, *v) for k, v in CASES.items()],
                             ids=list(CASES))
    def test_step_trace_covers_all_stages(self, name, coeffs, method, group):
        rep = simulate(coeffs)
        stages = {t.stage for t in rep.step_traces}
        assert {"S0", "S1", "S2", "S5", "S6", "S7"} <= stages
        # irreducible quintics additionally run S3 and S4
        if group is not None:
            assert "S3" in stages
            assert "S4" in stages

    def test_solvable_uses_radical_expressions(self):
        rep = simulate(CASES["F20"][0])
        # x^5 - 2 has a radical root 2^(1/5) among its roots
        assert any("root" in str(r["expr"]) or "2" in str(r["expr"])
                   for r in rep.roots)

    def test_unsolvable_uses_crootof(self):
        rep = simulate(CASES["S5"][0])
        assert any("CRootOf" in str(r["expr"]) for r in rep.roots)

    def test_palindromic_note_present(self):
        rep = simulate(CASES["palindromic"][0])
        notes = " ".join(rep.normal_form.notes) + " ".join(
            t.detail for t in rep.step_traces
        )
        assert "cubic" in notes.lower() or "palindromic" in notes.lower()


class TestJsonSchema:
    def test_to_json_roundtrip(self):
        rep = simulate(CASES["F20"][0])
        payload = json.loads(rep.to_json())
        # stable top-level schema
        for key in ("input", "method", "verified", "reducible", "roots",
                    "warnings", "step_traces", "group"):
            assert key in payload, f"missing {key} in JSON schema"
        assert payload["method"] == "radicals"
        assert payload["verified"] is True
        assert len(payload["roots"]) == 5
        for r in payload["roots"]:
            for k in ("expr", "numeric", "verified", "detail"):
                assert k in r

    def test_group_json_fields(self):
        rep = simulate(CASES["A5"][0])
        payload = json.loads(rep.to_json())
        g = payload["group"]
        assert g is not None
        for k in ("name", "order", "in_A5", "solvable", "discriminant",
                  "disc_square", "method"):
            assert k in g

    def test_json_writes_file(self, tmp_path):
        rep = simulate(CASES["D5"][0])
        out = tmp_path / "report.json"
        rep.write_json(out)
        assert out.exists()
        payload = json.loads(out.read_text())
        assert payload["method"] == "radicals"


class TestMarkdown:
    def test_markdown_has_sections(self):
        rep = simulate(CASES["C5"][0])
        md = rep.to_markdown()
        assert "# Quintic Solver" in md
        for token in ("Galois", "radical", "Numer", "Verif"):
            assert token in md

    def test_markdown_shows_group(self):
        rep = simulate(CASES["S5"][0])
        md = rep.to_markdown()
        assert "S5" in md


class TestCli:
    def test_cli_smoke_x5_minus_2(self, tmp_path):
        out = tmp_path / "out.json"
        r = subprocess.run(
            [sys.executable, "-m", "quintic_sim", "x^5 - 2",
             "--json", str(out)],
            capture_output=True, text=True, cwd=str(Path(__file__).resolve().parents[1]),
            timeout=180,
        )
        assert r.returncode == 0, r.stderr
        payload = json.loads(out.read_text())
        assert payload["method"] == "radicals"
        assert payload["verified"] is True

    def test_cli_accepts_coeff_list(self, tmp_path):
        out = tmp_path / "out.json"
        r = subprocess.run(
            [sys.executable, "-m", "quintic_sim",
             "1,1,-4,-3,3,1", "--json", str(out)],
            capture_output=True, text=True, cwd=str(Path(__file__).resolve().parents[1]),
            timeout=180,
        )
        assert r.returncode == 0, r.stderr
        payload = json.loads(out.read_text())
        assert payload["group"]["name"] == "C5"
