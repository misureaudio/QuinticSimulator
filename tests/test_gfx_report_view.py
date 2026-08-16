"""report_view.py — DocView: vertically-scrolling document with Treeview
tables (lateral scroll for wide rows).

These tests need a display (Windows desktop). They are skipped
automatically where tkinter cannot create a root window.
"""
import pytest

tk = pytest.importorskip("tkinter")

from quintic_sim_gfx.gui.mdrender import Table  # noqa: E402
from quintic_sim_gfx.gui.report_view import DocView  # noqa: E402


def _root():
    r = tk.Tk()
    r.withdraw()
    return r


def test_builds_and_renders_text():
    r = _root()
    v = DocView(r)
    v.render("# Title\n\n**Input:** `x**5`\n")
    r.update_idletasks()
    assert len(v._text_widgets) >= 1
    assert len(v.last_blocks) >= 2
    r.destroy()


def test_table_creates_treeview_with_columns():
    r = _root()
    v = DocView(r)
    v.render("| a | b |\n|---|---|\n| 1 | 2 |\n")
    r.update_idletasks()
    assert len(v._treeviews) == 1
    tree = v._treeviews[0]
    assert list(tree["columns"]) == ["c0", "c1"]
    assert tree.heading("c0", "text") == "a"
    assert tree.heading("c1", "text") == "b"
    r.destroy()


def test_table_row_count_and_values():
    r = _root()
    v = DocView(r)
    v.render("| a | b |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n| 5 | 6 |\n")
    r.update_idletasks()
    tree = v._treeviews[0]
    children = tree.get_children()
    assert len(children) == 3
    assert list(tree.item(children[0], "values")) == ["1", "2"]
    assert list(tree.item(children[2], "values")) == ["5", "6"]
    r.destroy()


def test_wide_table_has_lateral_scrollbar():
    r = _root()
    v = DocView(r)
    wide = "R" * 800
    v.render("| # | exact |\n|---|-------|\n| 0 | " + wide + " |\n")
    r.update_idletasks()
    tree = v._treeviews[0]
    xsb = v._xscrollbars[0]
    # the tree's xscrollcommand must be wired to a scrollbar command
    # (default is the empty string; a wired one ends in "set")
    cmd = tree.cget("xscrollcommand")
    assert cmd and cmd.endswith("set")
    assert str(xsb.cget("orient")) == "horizontal"
    # the wide column must be capped (overflow drives the scrollbar)
    width = tree.column("c1", "width")
    assert width <= v.MAX_COL
    r.destroy()


def test_clear_resets():
    r = _root()
    v = DocView(r)
    v.render("# A\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    r.update_idletasks()
    assert v._treeviews
    v.clear()
    r.update_idletasks()
    assert v._treeviews == []
    assert v._xscrollbars == []
    assert v.last_blocks == []
    r.destroy()


def test_real_report_fixture_renders():
    from pathlib import Path

    p = Path(__file__).resolve().parents[1] / "QuinticSolverReport_v0d.md"
    if not p.exists():
        pytest.skip("fixture report not present")
    r = _root()
    v = DocView(r)
    v.render(p.read_text(encoding="utf-8"))
    r.update_idletasks()
    tables = [b for b in v.last_blocks if isinstance(b, Table)]
    assert len(tables) == 2
    assert len(v._treeviews) == 2
    assert len(v._treeviews[0].get_children()) == 5   # roots
    assert len(v._treeviews[1].get_children()) == 9   # step trace
    r.destroy()
