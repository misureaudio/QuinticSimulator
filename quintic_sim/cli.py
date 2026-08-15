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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="quintic_sim",
        description=(
            "Quintic Solver Simulator: walks a degree-5 polynomial with "
            "rational coefficients through factorization, Galois-group "
            "classification, and the matching solution path."
        ),
    )
    ap.add_argument(
        "polynomial",
        help='polynomial as an expression ("x^5 - 2") or descending '
             "coefficient list (\"1,1,-4,-3,3,1\")",
    )
    ap.add_argument("--verbose", action="store_true",
                    help="print the full step trace to stderr")
    ap.add_argument("--sage", action="store_true",
                    help="enable the optional Sage-in-Docker cross-check")
    ap.add_argument("--json", metavar="FILE",
                    help="write the JSON report to FILE")
    args = ap.parse_args(argv)

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
    print(rep.to_markdown())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
