"""CLI — python -m quintic_sim "x^5 - 2" [--verbose] [--sage] [--json out.json]"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import sympy as sp

from .pipeline import simulate


def _parse_input(arg: str):
    """Parse a CLI argument: 'x^5 - 2' or '1,1,-4,-3,3,1'."""
    arg = arg.strip()
    if "," in arg:
        return [sp.Rational(t.strip()) for t in arg.split(",")]
    return sp.sympify(arg)


def _set_theme(name: str) -> None:
    """Persist the theme to the shared config (same file the GUI uses)."""
    from .gui import config as _gui_cfg  # tkinter-free: json/os/pathlib
    cfg = _gui_cfg.load()
    cfg["theme"] = name
    _gui_cfg.save(cfg)
    print(f"theme set to {name} (persisted to {_gui_cfg.config_path()})")


def _colorize(md: str, explicit) -> str:
    """Pick a palette (explicit flag > persisted config) and paint the
    markdown with ANSI colors — only when stdout is a terminal."""
    from . import ansi
    name = explicit
    if name is None:
        try:
            from .gui import config as _gui_cfg
            name = _gui_cfg.load().get("theme")
        except OSError:
            name = None
    if name not in ("light", "dark") or not ansi.color_enabled(sys.stdout):
        return md
    return ansi.paint_markdown(md, ansi.PALETTES[name])


def main(argv=None) -> int:
    # BEGIN Hermes/qwen3.8 27b
    # Windows consoles/pipes default to the ANSI code page (cp1252), which
    # cannot encode the report's ✅/⚠️/⊆ — force UTF-8 on the real streams.
    if sys.platform == "win32":
        import io
        for s in (sys.stdout, sys.stderr):
            if isinstance(s, io.TextIOWrapper):  # narrows the type; skips
                try:                             # replaced streams (tests)
                    s.reconfigure(encoding="utf-8")
                except (OSError, ValueError):    # detached/closed stream
                    pass
    # END Hermes/qwen3.8 27b
    ap = argparse.ArgumentParser(
        prog="quintic_sim",
        description=(
            "Quintic Solver Simulator: walks a degree-5 polynomial with "
            "rational coefficients through factorization, Galois-group "
            "classification, and the matching solution path."
        ),
    )
    ap.add_argument(
        "polynomial", nargs="?",
        help='polynomial as an expression ("x^5 - 2") or descending '
             'coefficient list ("1,1,-4,-3,3,1"); omit only with --set-theme',
    )
    ap.add_argument("--verbose", action="store_true",
                    help="print the full step trace to stderr")
    ap.add_argument("--sage", action="store_true",
                    help="enable the optional Sage-in-Docker cross-check")
    ap.add_argument("--json", metavar="FILE",
                    help="write the JSON report to FILE")
    ap.add_argument("--theme", choices=("light", "dark"),
                    help="ANSI color palette for this run's terminal output "
                         "(applies only when stdout is a terminal)")
    ap.add_argument("--set-theme", dest="set_theme", metavar="THEME",
                    choices=("light", "dark"),
                    help="persist the app theme (shared with the GUI) and use "
                         "it for this run; with no polynomial, just set and exit")
    try:
        args = ap.parse_args(argv)
        if args.polynomial is None and not args.set_theme:
            ap.error("polynomial is required (unless --set-theme is given)")
    except SystemExit as e:  # argparse errors (bad flag, missing poly)
        return int(e.code or 0)

    if args.set_theme:
        _set_theme(args.set_theme)
        if args.polynomial is None:
            return 0

    try:
        rep = simulate(_parse_input(args.polynomial), use_sage=args.sage)
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 2

    if args.verbose:
        for t in rep.step_traces:
            print(f"[{t.stage}] {t.name} ({t.duration:.3f}s): {t.detail}",
                  file=sys.stderr)

    if args.json:
        rep.write_json(Path(args.json))
        print(f"JSON report written to {args.json}")
    print(_colorize(rep.to_markdown(), args.theme or args.set_theme))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
