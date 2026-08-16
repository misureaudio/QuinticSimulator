# Quintic Solver Simulator

A Python simulator that walks a degree-5 polynomial with rational
coefficients through the *entire* decision tree of
[`QuinticMethods_v1.md`](../QuinticMethods_v1.md) — factorization,
Galois-group classification, and the matching solution path (radicals,
exact algebraic numbers, or numerics) — with a visible step-by-step trace
of every computational stage.

Theory ↔ implementation map: [`docs/algorithm-map.md`](docs/algorithm-map.md).

## GUI

A tkinter front-end lives in [`gui/`](gui/README.md). It is a wrapper
around this CLI: enter the 6 coefficients (default `0.0`), press Run, and
the markdown report renders in a scrollable pad where tables have their
own horizontal scrollbars (wide rows scroll laterally; double-click a
cell for its full text). The command it runs is user-configurable in the
window (and persisted to `%APPDATA%\quintic_sim_gfx\config.json`).

```bash
.venv/Scripts/python -m quintic_sim_gfx.gui
```

Requires `markdown-it-py` (see `requirements-gui.txt` at the project
root). The GUI process itself never imports sympy/numpy — all computation
runs in the subprocess.

## Install

Requires Python 3.11+ with `sympy`, `mpmath`, `numpy`, `pytest`.
A ready venv lives at `.venv-sym` in the project root.

Optional: Docker with the `sagemath/sagemath:latest` image for the
Galois-group cross-check (`--sage`). Without Docker the cross-check is
reported as `skipped` and everything else works unchanged.

## Usage

### CLI

```bash
# expression form
.venv-sym/Scripts/python -m quintic_sim "x^5 - 2*x^4 - 3*x^3 - 1" --verbose

# coefficient form (descending), with the optional Sage cross-check
.venv-sym/Scripts/python -m quintic_sim "1,0,0,0,0,-2" --sage --json out.json
```

Flags:

| flag | meaning |
|---|---|
| `--verbose` | print the step trace (stage, algorithm, timing) to stderr |
| `--sage` | enable the optional Sage-in-Docker Galois-group cross-check |
| `--json FILE` | write the machine-readable JSON report to FILE |

### Python API

```python
from quintic_sim import simulate
rep = simulate([1, 0, 0, 0, 0, -2], use_sage=True)
print(rep.method)          # 'radicals' | 'special' | 'reducible'
print(rep.group.name)      # C5 | D5 | F20 | A5 | S5 (None when reducible)
print(rep.verified)        # True iff every exact root passed the gate
for r in rep.roots:
    print(r["expr"], r["numeric"], r["verified"])
print(rep.to_markdown())   # human report
print(rep.to_json())       # machine report
```

## What it does (pipeline)

```
S0 input        parse -> monic primitive ZZ polynomial, squarefree split
S1 normal form  depressed quintic; palindromic detection + reduction
S2 factor       rational-root test + Zassenhaus (SymPy factor_list)
S3 Galois group SymPy galois_group (Cohen Alg 6.3.9 quintic hybrid)
                + optional Sage-in-Docker cross-check
S4 dispatch     solvable  -> radicals (F20 resolvent + Lagrange resolvents)
                unsolvable-> CRootOf exact forms + Bring-radical notation
                reducible -> classical formulas for each factor
S5 numerics     mpmath Aberth (50 digits) + NumPy companion + Durand-Kerner
S6 gate         residual < 1e-30 (40 digits) + cross-match vs numerics
S7 report       Markdown + JSON with full step trace and timings
```

Every exact root is a **hypothesis until the S6 gate certifies it**: a
40-digit residual check plus an independent numeric cross-match. Failed
roots are replaced by `CRootOf` forms and the report carries a warning.

## Test suite

```bash
.venv-sym/Scripts/python -m pytest tests/ -v
```

207 tests: unit tests per stage, the 8+1 verified test vectors
end-to-end, a 200-quintic Galois invariant property test
(`disc square ⟺ G ⊆ A5`), a 50-quintic mpmath-vs-NumPy property test,
and the real Docker cross-check (skipped automatically when Docker is
absent) — plus the GUI suite (`tests/test_gfx_*.py`: headless unit tests,
widget tests, and end-to-end runs through the real CLI, including the
Sage-in-Docker cross-check).

## Honest limitations (v1)

- **Bring radical** is *notation only* — no open-source CAS implements
  `Br(·)` as a callable.
- **Klein's icosahedral solution** is a documented stub — no open-source
  Schwarz-triangle-function implementation of the general quintic exists.
- **Bring-Jerrard reduction** is not computed (coefficient blow-up
  risk); the pipeline never needs the form.
- **Aberth** degrades on multiple roots; the pipeline falls back to the
  NumPy companion-matrix eigenvalues (machine precision) and the gate
  adapts its cross-match tolerance accordingly.
