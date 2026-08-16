"""Tests for the optional Sage-in-Docker cross-check bridge."""

import json
import shutil
import subprocess

import pytest

from quintic_sim.sage_bridge import (
    GROUP_NUMBER_TO_NAME,
    SageResult,
    classify_with_sage,
    docker_available,
)

# (coeffs descending, expected transitive group number, expected name)
VECTORS = [
    ([1, 1, -4, -3, 3, 1], 1, "C5"),
    ([1, -2, -3, 0, 0, -1], 2, "D5"),
    ([1, 0, 0, 0, 0, -2], 3, "F20"),
    ([1, -2, -1, -3, 2, -3], 4, "A5"),
    ([1, 0, 0, -5, 5, 1], 5, "S5"),
]


def _docker_here() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        r = subprocess.run(
            ["docker", "image", "inspect", "sagemath/sagemath:latest"],
            capture_output=True, timeout=30,
        )
        return r.returncode == 0
    except Exception:
        return False


DOCKER = _docker_here()


class TestMappingTable:
    def test_number_to_name(self):
        assert GROUP_NUMBER_TO_NAME == {1: "C5", 2: "D5", 3: "F20", 4: "A5", 5: "S5"}


class TestDockerAvailable:
    def test_reports_boolean(self):
        assert isinstance(docker_available(), bool)
        assert docker_available() == DOCKER


@pytest.mark.skipif(not DOCKER, reason="Docker/sagemath image not available")
class TestSageCrossCheck:
    @pytest.mark.parametrize("coeffs,number,name", VECTORS)
    def test_all_five_vectors_agree(self, coeffs, number, name):
        r = classify_with_sage(coeffs)
        assert r.status == "ok"
        assert r.group_number == number
        assert r.name == name
        assert r.solvable == (name in ("C5", "D5", "F20"))

    def test_result_is_dataclass(self):
        r = classify_with_sage(VECTORS[0][0])
        assert isinstance(r, SageResult)


class TestGracefulDegradation:
    def test_no_docker_gives_skipped(self, monkeypatch):
        # simulate docker being absent
        monkeypatch.setattr("quintic_sim.sage_bridge.shutil.which", lambda _: None)
        r = classify_with_sage([1, 0, 0, 0, 0, -2])
        assert r.status == "skipped"
        assert r.name is None
        assert "docker" in r.detail.lower()

    def test_timeout_gives_error(self, monkeypatch):
        # simulate a hung docker call (and a present docker, so it reaches the call)
        monkeypatch.setattr("quintic_sim.sage_bridge.docker_available", lambda: True)

        def fake_run(cmd, **kw):
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=1)
        monkeypatch.setattr(
            "quintic_sim.sage_bridge.subprocess.run", fake_run
        )
        r = classify_with_sage([1, 0, 0, 0, 0, -2], timeout=1)
        assert r.status == "error"
        assert r.name is None

    def test_bad_json_gives_error(self, monkeypatch):
        monkeypatch.setattr("quintic_sim.sage_bridge.docker_available", lambda: True)

        class FakeProc:
            returncode = 0
            stdout = "garbage with no json at all\n"
            stderr = ""
        monkeypatch.setattr(
            "quintic_sim.sage_bridge.subprocess.run", lambda cmd, **kw: FakeProc()
        )
        r = classify_with_sage([1, 0, 0, 0, 0, -2])
        assert r.status == "error"
