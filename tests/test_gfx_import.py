"""The parent package must stay importable without loading numpy/sympy,
so the GUI process (which never does math in-process) is light and immune
to numpy-ABI problems. The public API must keep working via lazy getattr.

The isolation check runs in a *fresh interpreter* (subprocess), because
pytest itself may have loaded numpy at collection time via other test
modules — an in-process sys.modules check would be order-dependent.
"""
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _fresh_interpreter(code: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_import_package_does_not_load_numpy_or_sympy():
    res = _fresh_interpreter(
        "import sys, quintic_sim_gfx;"
        "assert 'numpy' not in sys.modules, 'numpy loaded by package import';"
        "assert 'sympy' not in sys.modules, 'sympy loaded by package import'"
    )
    assert res.returncode == 0, res.stderr


def test_import_gui_subpackage_does_not_load_numpy():
    res = _fresh_interpreter(
        "import sys, quintic_sim_gfx.gui;"
        "assert 'numpy' not in sys.modules, 'numpy loaded by gui import'"
    )
    assert res.returncode == 0, res.stderr


def test_public_api_still_exposed():
    from quintic_sim_gfx import PipelineError, Report, StepTrace, simulate  # noqa: F401

    assert callable(simulate)
    # importing the public API *does* pull in the pipeline (and numpy) —
    # that is the CLI/subprocess path, which is fine.
    assert "numpy" in sys.modules


def test_unknown_attribute_raises():
    import quintic_sim_gfx

    with pytest.raises(AttributeError):
        quintic_sim_gfx.definitely_not_here
