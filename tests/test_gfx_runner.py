"""runner.py — coefficient parsing, expression formatting, command building,
PYTHONPATH-scrubbing subprocess execution."""
import os
from fractions import Fraction

from quintic_sim_gfx.gui import runner


# ---------------------------------------------------------------------------
# parse_coeff
# ---------------------------------------------------------------------------
def test_parse_coeff_ints():
    assert runner.parse_coeff("0.0") == 0
    assert runner.parse_coeff("-2") == -2
    assert runner.parse_coeff(" 3 ") == 3


def test_parse_coeff_decimals_and_fractions():
    assert runner.parse_coeff("2.5") == Fraction(5, 2)
    assert runner.parse_coeff("1/2") == Fraction(1, 2)
    assert runner.parse_coeff("-1e2") == -100


def test_parse_coeff_empty_is_zero():
    assert runner.parse_coeff("") == 0
    assert runner.parse_coeff("   ") == 0


def test_parse_coeff_garbage_raises():
    for bad in ("abc", "x^2", "1/0", "1.2.3", "2 3"):
        try:
            runner.parse_coeff(bad)
            raise AssertionError(f"{bad!r} should have raised")
        except ValueError:
            pass


# ---------------------------------------------------------------------------
# format_polynomial
# ---------------------------------------------------------------------------
def test_format_matches_user_example():
    expr, err = runner.format_polynomial([1, -2, -3, 0, 0, -1])
    assert err is None
    assert expr == "x^5 - 2*x^4 - 3*x^3 - 1"


def test_format_monic_and_simple():
    assert runner.format_polynomial([1, 0, 0, 0, 0, -2])[0] == "x^5 - 2"
    assert runner.format_polynomial([1, 1, -4, -3, 3, 1])[0] == (
        "x^5 + x^4 - 4*x^3 - 3*x^2 + 3*x + 1"
    )


def test_format_negative_leading_and_unit_coeffs():
    assert runner.format_polynomial([-1, 0, 0, 0, 0, 0])[0] == "-x^5"
    # unit coefficients on x and x^2 drop the "1*" factor
    assert runner.format_polynomial([1, 0, 0, 0, 1, 0])[0] == "x^5 + x"
    assert runner.format_polynomial([1, 0, 0, 0, -1, 0])[0] == "x^5 - x"
    assert runner.format_polynomial([1, 0, 0, 1, 0, 0])[0] == "x^5 + x^2"


def test_format_fraction_coeff():
    expr, _ = runner.format_polynomial([1, 0, 0, 0, 0, Fraction(1, 2)])
    assert expr == "x^5 + 1/2"


def test_format_zero_x_term_dropped():
    expr, _ = runner.format_polynomial([1, 0, 0, -5, 0, 1])
    assert expr == "x^5 - 5*x^2 + 1"


def test_format_rejects_all_zero():
    assert runner.format_polynomial([0, 0, 0, 0, 0, 0])[1] is not None


def test_format_rejects_non_quintic():
    assert runner.format_polynomial([0, 1, 0, 0, 0, 0])[1] is not None
    assert runner.format_polynomial([1, 0, 0, 0, 0, 0, 0])[1] is not None


def test_format_expression_is_sympy_parseable():
    # the whole point: the CLI must accept what we generate
    import sympy as sp

    coeffs = [1, -2, -3, 0, 0, -1]
    expr, err = runner.format_polynomial(coeffs)
    assert err is None
    x = sp.Symbol("x")
    got = sp.Poly(sp.sympify(expr), x).all_coeffs()
    assert [int(c) for c in got] == [c for c in coeffs]


# ---------------------------------------------------------------------------
# format_coeff_list
# ---------------------------------------------------------------------------
def test_format_coeff_list():
    assert runner.format_coeff_list([1, -2, -3, 0, 0, -1]) == "1,-2,-3,0,0,-1"
    assert runner.format_coeff_list([1, 0, 0, 0, 0, Fraction(1, 2)]) == "1,0,0,0,0,1/2"


# ---------------------------------------------------------------------------
# clean_env (the PYTHONPATH pitfall)
# ---------------------------------------------------------------------------
def test_clean_env_scrubs_hermes_entries(monkeypatch):
    monkeypatch.setenv(
        "PYTHONPATH",
        "C:\\Users\\misur\\AppData\\Local\\hermes\\hermes-agent"
        + os.pathsep
        + "C:\\Users\\misur\\AppData\\Local\\hermes\\hermes-agent\\venv\\Lib\\site-packages"
        + os.pathsep
        + "/keep/this",
    )
    env = runner.clean_env()
    assert "hermes-agent" not in env.get("PYTHONPATH", "")
    assert "/keep/this" in env["PYTHONPATH"]


def test_clean_env_drops_var_when_empty(monkeypatch):
    monkeypatch.setenv("PYTHONPATH", "only/hermes-agent/venv")
    env = runner.clean_env()
    assert "PYTHONPATH" not in env


def test_clean_env_without_var(monkeypatch):
    monkeypatch.delenv("PYTHONPATH", raising=False)
    env = runner.clean_env()
    assert "PYTHONPATH" not in env
    # everything else preserved
    assert env.get("PATH") == os.environ.get("PATH")


# ---------------------------------------------------------------------------
# build_command
# ---------------------------------------------------------------------------
def test_build_command_substitutes_and_quotes():
    argv = runner.build_command("python -m quintic_sim {poly} --sage", "x^5 - 2")
    assert argv == ["python", "-m", "quintic_sim", "x^5 - 2", "--sage"]


def test_build_command_quotes_poly_with_spaces():
    argv = runner.build_command("py -m q {poly}", "x^5 + 1/2")
    assert argv == ["py", "-m", "q", "x^5 + 1/2"]


def test_build_command_sage_toggle():
    with_sage = runner.build_command("py -m q {poly} --sage", "x^5-2", sage=True)
    no_sage = runner.build_command("py -m q {poly} --sage", "x^5-2", sage=False)
    assert "--sage" in with_sage
    assert "--sage" not in no_sage


def test_build_command_without_placeholder_unchanged():
    argv = runner.build_command("py script.py --flag", "x^5")
    assert argv == ["py", "script.py", "--flag"]
