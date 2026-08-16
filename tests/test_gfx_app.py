"""app.py — main window wiring (panel -> subprocess -> DocView).

Widget tests need a display; the end-to-end test additionally runs the
real CLI in a subprocess (no --sage, so it stays fast).
"""
import time

import pytest

tk = pytest.importorskip("tkinter")

from quintic_sim_gfx.gui.app import QuinticApp  # noqa: E402
from quintic_sim_gfx.gui.mdrender import Table  # noqa: E402


def _root():
    r = tk.Tk()
    r.withdraw()
    return r


def _pump(app, root, until, timeout=45.0):
    """Spin the main loop until `until()` is true or timeout."""
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        root.update()
        if until():
            return True
        time.sleep(0.05)
    return False


def test_app_builds():
    r = _root()
    app = QuinticApp(r)
    r.update_idletasks()
    assert app.doc is not None and app.panel is not None
    assert "quintic_sim" in app.cmd_var.get()
    assert app.doc.last_blocks[0].inlines[0][1] == "Ready"
    r.destroy()


def test_render_roundtrip_without_subprocess():
    r = _root()
    app = QuinticApp(r)
    app.doc.render("| # | exact |\n|---|-------|\n| 0 | x |\n")
    r.update_idletasks()
    assert len(app.doc._treeviews) == 1
    r.destroy()


def test_on_run_rejects_non_quintic_in_statusbar():
    from fractions import Fraction

    r = _root()
    app = QuinticApp(r)
    app.on_run([Fraction(0), Fraction(1), Fraction(0),
                Fraction(0), Fraction(0), Fraction(0)])
    r.update_idletasks()
    assert "c5 is zero" in app.status.cget("text")
    assert app.status.cget("text").startswith("\u26a0")
    r.destroy()


def test_on_done_error_path_renders_error_block():
    from quintic_sim_gfx.gui.runner import RunResult

    r = _root()
    app = QuinticApp(r)
    app._on_done(RunResult(False, "", "boom: something failed", 2, 0.1, "cmd"))
    r.update_idletasks()
    assert app.status.cget("text").startswith("FAILED")
    # the error was rendered as a fenced code block in the doc
    assert any("boom" in b.text for b in app.doc.last_blocks
               if type(b).__name__ == "CodeBlock")
    r.destroy()


def test_gui_end_to_end_no_sage():
    """The full pipeline: boxes -> command -> subprocess -> rendered tables."""
    from fractions import Fraction

    r = _root()
    app = QuinticApp(r)
    # fast path: no --sage (the subprocess still does the real work)
    app.cmd_var.set(".venv/Scripts/python -m quintic_sim {poly}")
    app.sage_var.set(False)
    coeffs = [1, -2, -3, 0, 0, -1]  # x^5 - 2x^4 - 3x^3 - 1 (D5, solvable)
    app.panel.set_coeffs(coeffs)
    r.update_idletasks()
    assert app.panel.preview_text().strip() == "f(x) = x^5 - 2*x^4 - 3*x^3 - 1"

    app.on_run([Fraction(c) for c in coeffs])
    ok = _pump(app, r, lambda: app.status.cget("text").startswith(("OK", "FAILED")))
    assert ok, "worker did not finish in time: " + app.status.cget("text")
    assert app.status.cget("text").startswith("OK"), app.status.cget("text")
    r.update_idletasks()

    tables = [b for b in app._last_blocks if isinstance(b, Table)]
    assert len(tables) == 2
    roots = tables[0]
    assert len(roots.rows) == 5
    assert all(len(row) == 4 for row in roots.rows)
    # every root row carries a numeric value in column 2
    from quintic_sim_gfx.gui.mdrender import runs_text
    for row in roots.rows:
        assert runs_text(row[2]).strip() != ""
    r.destroy()


def test_gui_end_to_end_sage_skips_without_docker():
    import shutil

    if shutil.which("docker") is None:
        pytest.skip("docker not available")
    from fractions import Fraction

    r = _root()
    app = QuinticApp(r)
    app.cmd_var.set(".venv/Scripts/python -m quintic_sim {poly} --sage")
    app.sage_var.set(True)
    app.on_run([Fraction(c) for c in [1, -2, -3, 0, 0, -1]])
    ok = _pump(app, r, lambda: app.status.cget("text").startswith(("OK", "FAILED")),
               timeout=300)
    assert ok
    assert app.status.cget("text").startswith("OK"), app.status.cget("text")
    r.destroy()
