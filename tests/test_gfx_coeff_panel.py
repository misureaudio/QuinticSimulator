"""coeff_panel.py — the six coefficient boxes + live preview + buttons.

Needs a display (Windows desktop); skipped automatically where tkinter
cannot create a root window.
"""
import pytest

tk = pytest.importorskip("tkinter")

from quintic_sim_gfx.gui.coeff_panel import CoeffPanel  # noqa: E402


def _root():
    r = tk.Tk()
    r.withdraw()
    return r


def test_defaults_are_zero():
    r = _root()
    p = CoeffPanel(r, on_run=lambda c: None, on_stop=None, on_clear=None)
    r.update_idletasks()
    assert p.get_coeffs_text() == ["0.0"] * 6
    r.destroy()


def test_set_and_get():
    r = _root()
    p = CoeffPanel(r, on_run=lambda c: None, on_stop=None, on_clear=None)
    p.set_coeffs([1, -2, -3, 0, 0, -1])
    r.update_idletasks()
    assert p.get_coeffs_text() == ["1", "-2", "-3", "0", "0", "-1"]
    r.destroy()


def test_preview_matches_user_example():
    r = _root()
    p = CoeffPanel(r, on_run=lambda c: None, on_stop=None, on_clear=None)
    p.set_coeffs([1, -2, -3, 0, 0, -1])
    r.update_idletasks()
    assert p.preview_text().strip() == "f(x) = x^5 - 2*x^4 - 3*x^3 - 1"
    r.destroy()


def test_preview_shows_error_for_non_quintic():
    r = _root()
    p = CoeffPanel(r, on_run=lambda c: None, on_stop=None, on_clear=None)
    p.set_coeffs([0, 1, 0, 0, 0, 0])
    r.update_idletasks()
    assert "c5 is zero" in p.preview_text()
    r.destroy()


def test_invalid_input_shows_error_not_crash():
    r = _root()
    p = CoeffPanel(r, on_run=lambda c: None, on_stop=None, on_clear=None)
    p.entries[0].delete(0, tk.END)
    p.entries[0].insert(0, "abc")
    r.update_idletasks()
    p._update_preview()  # must not raise
    assert "invalid" in p.preview_text().lower()
    r.destroy()


def test_run_passes_rationals_to_callback():
    from fractions import Fraction

    r = _root()
    got = []
    p = CoeffPanel(r, on_run=lambda c: got.append(c), on_stop=None,
                   on_clear=None)
    p.set_coeffs([1, 0, 0, 0, 0, Fraction(1, 2)])
    r.update_idletasks()
    p.run()
    assert got == [[1, 0, 0, 0, 0, Fraction(1, 2)]]
    r.destroy()


def test_run_with_bad_input_does_not_call_callback():
    r = _root()
    got = []
    p = CoeffPanel(r, on_run=lambda c: got.append(c), on_stop=None,
                   on_clear=None)
    p.entries[3].delete(0, tk.END)
    p.entries[3].insert(0, "xyz")
    p.run()
    assert got == []
    r.destroy()


def test_set_running_toggles_buttons():
    r = _root()
    p = CoeffPanel(r, on_run=lambda c: None, on_stop=None, on_clear=None)
    r.update_idletasks()
    assert str(p.run_btn.cget("state")) == "normal"
    p.set_running(True)
    assert str(p.run_btn.cget("state")) == "disabled"
    assert str(p.stop_btn.cget("state")) == "normal"
    p.set_running(False)
    assert str(p.run_btn.cget("state")) == "normal"
    assert str(p.stop_btn.cget("state")) == "disabled"
    r.destroy()


def test_clear_resets_to_defaults():
    r = _root()
    p = CoeffPanel(r, on_run=lambda c: None, on_stop=None, on_clear=None)
    p.set_coeffs([1, 2, 3, 4, 5, 6])
    r.update_idletasks()
    p._clear()
    r.update_idletasks()
    assert p.get_coeffs_text() == ["0.0"] * 6
    r.destroy()
