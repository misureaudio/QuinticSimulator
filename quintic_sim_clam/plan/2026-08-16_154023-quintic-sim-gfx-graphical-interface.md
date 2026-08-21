# Quintic Sim GFX — Graphical Interface Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Add a desktop GUI to `quintic_sim_gfx/` that (1) lets the user type the 6 coefficients of a degree-5 polynomial into input boxes (default `0.0`) and (2) renders the resulting markdown report in a scrollable "output pad" with a readable, laterally-scrollable table layout — implemented as a thin **wrapper around a user-configurable shell command** (default the verified `.venv/Scripts/python -m quintic_sim <poly> --sage`).

**Architecture:** A new `quintic_sim_gfx/gui/` subpackage. The GUI process is deliberately **lightweight**: it imports only `tkinter` (stdlib) + `markdown-it-py` and never imports `sympy`/`numpy`. All heavy computation is delegated to a **subprocess** running the user-configured command. The subprocess `stdout` (the markdown report) is tokenized with `markdown-it-py` and rendered into a vertically-scrolling document where **each markdown table becomes a `ttk.Treeview`** (native lateral scrollbar, wide-cell handling, double-click-to-expand). The parent package `__init__.py` is made lazy (PEP 562) so importing the GUI never drags in `numpy`.

**Tech Stack:** Python 3.13 (`.venv`), `tkinter`/`ttk` (stdlib, verified present), `markdown-it-py 4.2.0` (pure-Python, **already in `.venv`**), `fractions`/`subprocess`/`shlex` (stdlib). Alternatives evaluated in §3.

---

## 1. Context and verified assumptions

The following were **actually executed and verified on this machine** before this plan was written:

| # | Fact | How verified |
|---|------|--------------|
| V1 | `quintic_sim_gfx/` is a **byte-identical copy** of the working `quintic_sim/` package (same 148-test pipeline: `cli.py, input.py, normalform.py, factor.py, galois.py, radicals.py, special.py, numeric.py, verify.py, report.py, pipeline.py, sage_bridge.py, errors.py`, `__init__.py`, `__main__.py`) **plus** two extra subdirs: `docs/` (algorithm-map.md/.pdf) and `plan/` (the original architecture plan). It is **untracked** in git (`?? quintic_sim_gfx/`). | `diff -rq quintic_sim quintic_sim_gfx` → only `docs` and `plan` differ; `git status` shows `?? quintic_sim_gfx/`. |
| V2 | The CLI the GUI must wrap is `.venv/Scripts/python -m quintic_sim <polyexpr> [--verbose] [--sage] [--json FILE]`. `<polyexpr>` is **either** an expression (`"x^5 - 2*x^4 - 3*x^3 - 1"`) **or** a descending comma coefficient list (`"1,1,-4,-3,3,1"`). `--sage` enables the optional Sage-in-Docker cross-check. `stdout` = markdown report; `stderr` = verbose trace / `error: …`; exit `0` success, `2` on error. | Read `quintic_sim_gfx/cli.py`; ran `env -u PYTHONPATH .venv/Scripts/python -m quintic_sim "x^5 - 2*x^4 - 3*x^3 - 1"` → full markdown report, exit 0. |
| V3 | The markdown report contains **two tables**. (a) *Roots (S4/S5)*: `| # | exact | numeric (15 digits) | verified |` — the **`exact` column is extremely wide** (radical expressions, hundreds of characters, no spaces). (b) *Step trace*: `| stage | step | detail | time (s) |` — the **`detail` column is wide**. It also uses `#`/`##` headings, `**bold**`, inline `` `code` ``, `>` blockquotes (palindromic reduction), and `- ` bullet lists (factorization notes, warnings). No fenced code blocks. | Read `quintic_sim_gfx/report.py`; read a real report `QuinticSolverReport_v0d.md`. |
| V4 | `.venv` is **Python 3.13.14** and (after the user's upgrades) contains `sympy 1.14.0`, `mpmath 1.3.0`, `numpy 2.5.1`, `PIL 12.3.0`, `tkinter 8.6`/`ttk` (stdlib, bundled with the Windows CPython install — **no pip install needed**; `ttk` is a submodule of `tkinter`), **`markdown-it-py 4.2.0`**, `markdown 3.10.3`, `pygments 2.20.0`, and **`customtkinter 6.0.0`** (optional theming layer; note it has **no `CTkTreeview`** — tables still use plain `ttk.Treeview`). It does **NOT** contain `PySide6`, `PyQt5/6`. The markdown deps are preinstalled — Task 1 is a verification, not an install. | `env -u PYTHONPATH .venv/Scripts/python -c "import …"` per module (re-run after each venv upgrade; widget smoke test of ttk.Frame/Entry/Button/Treeview/Scrollbar passed). |
| V5 | **CRITICAL PITFALL — `PYTHONPATH` pollution.** This agent shell has `PYTHONPATH=C:\Users\misur\AppData\Local\hermes\hermes-agent;…\hermes-agent\venv\Lib\site-packages`. That venv holds a **cp311** `numpy 2.4.3`. Because `PYTHONPATH` entries precede the project venv on `sys.path`, `import numpy` under `.venv/Scripts/python` (cp313) finds the cp311 binary and **crashes** with `ModuleNotFoundError: No module named 'numpy._core._multiarray_umath'`. Running with `env -u PYTHONPATH` (or scrubbing those entries) makes the exact same command succeed. **Any subprocess the GUI spawns must scrub the hermes-agent `PYTHONPATH` entries**, or the child `quintic_sim` will die at `import numpy`. | Ran the CLI with and without the polluted `PYTHONPATH`; the failure/success diff is exactly the numpy ABI error. |
| V6 | `markdown-it-py` (v4.2.0, pure-Python) tokenizes the report into a **flat, paired token stream**. Verified exact token types: `heading_open/inline/heading_close` (`t.tag` = `h1`..`h6`), `paragraph_open/inline/paragraph_close`, `table_open/thead_open/tr_open/th_open|td_open/inline/th_close|td_close/tr_close/thead_close/tbody_open/…/tbody_close/table_close`, plus `blockquote_*`, `bullet_list_open/list_item_open`, `fence`/`code_block`, `hrule`. Inline children (inside `t.children` of the `inline` token) use `text`, `code_inline`, `strong_open/close`, `em_open/close`, `softbreak`. Tables are enabled with `MarkdownIt("commonmark").enable("table")`. | Ran `MarkdownIt('commonmark').enable('table').parse(sample_report)` (re-verified on v4.2.0 after the venv upgrade; token stream unchanged) and printed the full token list; the structure matched the parser design in this plan exactly. |
| V7 | The GUI process must **not** import `sympy`/`numpy`. As written, `quintic_sim_gfx/__init__.py` does `from .pipeline import simulate` (→ imports `numpy`). Importing the subpackage `quintic_sim_gfx.gui` would trigger that parent `__init__`. Making the parent `__init__` **lazy** (PEP 562 `__getattr__`) keeps the GUI process light and immune to the V5 numpy ABI issue in-process, while preserving the public API (`from quintic_sim_gfx import simulate`). | Reasoning over import order; `__init__.py` content read. |

**Test vector suite** (from quintic_sim_gfx/plan/…-architecture.md §1; all previously verified end-to-end). Used by the GUI end-to-end test:

| Class | Polynomial (expression form) | Descending coeffs |
|---|---|---|
| C5 | `x^5 + x^4 - 4*x^3 - 3*x^2 + 3*x + 1` | `1,1,-4,-3,3,1` |
| D5 | `x^5 - 2*x^4 - 3*x^3 - 1` | `1,-2,-3,0,0,-1` |
| F20 | `x^5 - 2` | `1,0,0,0,0,-2` |
| A5 | `x^5 - 2*x^4 - x^3 - 3*x^2 + 2*x - 3` | `1,-2,-1,-3,2,-3` |
| S5 | `x^5 - 5*x^2 + 5*x + 1` | `1,0,0,-5,5,1` |
| Reducible | `(x-1)(x^4+2x^3+3x^2+4x+5)` | expand at run-time |
| Palindromic | `x^5 + 2*x^4 - 3*x^3 - 3*x^2 + 2*x + 1` | `1,2,-3,-3,2,1` |
| Rational root | `x^5 - 6*x^4 + 13*x^3 - 12*x^2 + 5*x - 1` | `1,-6,13,-12,5,-1` |

---

## 2. Requirements (restated)

1. **Coefficient input panel** — a subsection of the main window with **6 input boxes**, one per power of `x` in **descending** order: `[c5] x^5 + [c4] x^4 + [c3] x^3 + [c2] x^2 + [c1] x + [c0]`. Default value `0.0` in every box. A live preview shows the assembled expression (e.g. `x^5 - 2*x^4 - 3*x^3 - 1`).
2. **Output pad** — renders the markdown report with a **readable table layout**; **supports lateral (horizontal) scrolling** and must **accommodate wide tables/rows** (the radical `exact` column).
3. **Command wrapper** — the GUI drives a **user-configurable command** (persisted), default the verified `.venv/Scripts/python -m quintic_sim {poly} --sage`. The GUI builds the polynomial from the boxes, substitutes it into the command, runs it in a subprocess, and renders `stdout`.

---

## 3. Framework & rendering decision (options evaluated)

### 3.1 GUI toolkit

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **tkinter + ttk** | stdlib (V4: verified present); zero install; `ttk.Treeview` is the *native* wide-table widget with built-in horizontal + vertical scrollbars; small, stable. | Dated look; no built-in markdown. | **CHOSEN.** Best fit for "readable table layout + lateral scrolling" with no heavy deps. |
| PySide6 / PyQt6 + `QWebEngineView` | Render markdown as real HTML in a Chromium engine — best visual fidelity; tables scroll natively. | **Missing from venv** (V4); ~500 MB + a Chromium runtime; overkill for a 2-table report. | Rejected as default; viable upgrade if the user later wants full HTML fidelity. |
| Web app (Flask/FastAPI + browser) | Best table rendering; trivially wide/scrollable. | Different architecture (server + browser), not a single-window desktop "wrapper"; the user framed this as a main-window desktop GUI. | Rejected; noted as an alternative if the user prefers a browser. |
| customtkinter | Prettier modern theme. | **Missing from venv** (V4); still no markdown renderer (would still need the Treeview approach). | Optional theme-only layer; not required. |

### 3.2 Markdown parser

| Option | Verdict |
|---|---|
| **markdown-it-py** | **CHOSEN.** Pure-Python, small, well-maintained, CommonMark + GFM tables (V6: token stream verified). The only new hard dependency (`pip install markdown-it-py`). |
| python-markdown / mistune / commonmark | Produce HTML or a different AST; we want a lightweight block model to drive `ttk` widgets, not HTML. Rejected. |

### 3.3 Table rendering inside the output pad

| Option | Verdict |
|---|---|
| **`ttk.Treeview` per table** | **CHOSEN.** Native `xscroll`/`yscroll`, per-column widths, header row, row striping. Wide `exact` cells are clipped at the column edge → the table's own horizontal scrollbar appears. Double-click a cell → popup with the full wrapped text. This most directly satisfies "readable table layout", "lateral scrolling", "wide rows". |
| Label-grid on a 2D-scrolling `Canvas` | Cells can wrap; single horizontal scrollbar for the whole doc. Less "table-like", more layout code. Kept as an optional enhancement (§8). |
| HTML-in-CEF / QWebEngine | Best fidelity, needs missing deps. Rejected (see 3.1). |

**Design consequence:** the output pad is a **vertically-scrolling document** (a `Canvas` + vertical `Scrollbar` wrapping an inner `Frame`). Each markdown *table* is embedded as a `ttk.Treeview` with **its own horizontal scrollbar** (lateral scroll per table); headings/paragraphs/quotes/lists are styled `tk.Text`/`Label` blocks. The wide radical column triggers the table's horizontal scrollbar.

**Implementation note (deviation, verified during build):** the original design marshalled results with `root.after(0, ...)` called from the worker thread. On **Python 3.13 / Windows this raises `RuntimeError: main thread is not in main loop`** (thread-registered Tcl commands are rejected). The implemented handoff instead uses a **thread-safe `queue.Queue` outbox**: the worker only `put`s the `RunResult`; the main loop drains it via a 100 ms `root.after` poll that stops when idle. The worker also captures `StringVar`/`BooleanVar` values on the main thread before starting (tkinter variables are not thread-safe).

---

## 4. Architecture overview

```
quintic_sim_gfx/                      (existing package — copy of quintic_sim)
  __init__.py        [MODIFY] make lazy (PEP 562) so importing gui/ never loads numpy
  __main__.py        (unchanged — CLI entry)
  cli.py … report.py (unchanged — the pipeline)
  docs/, plan/       (unchanged)
  gui/               [NEW subpackage]
    __init__.py          [NEW]
    __main__.py          [NEW]  python -m quintic_sim_gfx.gui  → launches the app
    config.py            [NEW]  load/save the user-configurable command template (JSON)
    runner.py            [NEW]  coeffs→expression formatter, command builder,
                                PYTHONPATH-scrubbing subprocess worker, RunResult
    mdrender.py          [NEW]  markdown-it-py tokens → block model (Heading/Paragraph/
                                Table/Quote/List/CodeBlock/HRule) — no tkinter import
    report_view.py       [NEW]  DocView: vertically-scrolling document; renders blocks;
                                each Table → ttk.Treeview (lateral scroll) + expand popup
    coeff_panel.py       [NEW]  the 6 coefficient boxes + live expression preview + Run/Stop/Clear
    app.py               [NEW]  QuinticApp: main window, layout, worker thread, status bar
```

**Data flow**

```
[6 coefficient boxes] --parse(Fraction)--> coeffs (c5..c0)
        |
        v
runner.format_polynomial(coeffs) --> "x^5 - 2*x^4 - 3*x^3 - 1"   (or comma list)
        |
        v
runner.build_command(template, poly) --> argv  (template = ".venv/Scripts/python -m quintic_sim {poly} --sage")
        |
        v
runner.run_command(argv)  --subprocess, scrubbed PYTHONPATH, cwd=project root, Popen (killable)-->
        |
        v
RunResult(ok, stdout=markdown, stderr, returncode, duration)
        |  (marshalled to the main thread via root.after)
        v
mdrender.render_blocks(markdown) --> [Block, …]
        |
        v
report_view.DocView.add_block(block)  -->  styled Text / Label / ttk.Treeview (per table, lateral scroll)
```

**Dependency policy**

- GUI process requires only: `tkinter` (stdlib), `markdown-it-py` (already in `.venv`, V4). **No `sympy`/`numpy` in-process** (enforced by the lazy `__init__`, V7).
- The **subprocess** (the wrapped command) needs the full pipeline env (`.venv` with sympy/mpmath/numpy) — same as the verified CLI.
- Optional: Docker + `sagemath/sagemath:latest` for the `--sage` cross-check (degrades gracefully, unchanged from the CLI).

---

## 5. Step-by-step tasks

> Conventions: run everything with the **clean** interpreter `env -u PYTHONPATH .venv/Scripts/python …` (V5). Tests live in the existing top-level `tests/` as `tests/test_gfx_*.py`. Commit after each task.

### Task 1: Verify the markdown dependency is present

**Objective:** Confirm `markdown-it-py` is importable in the project venv (it is preinstalled after the venv upgrade, V4 — no install needed).

**Step 1: Verify import (clean env)**
```bash
cd C:/Users/misur/source/hermes-dir
env -u PYTHONPATH .venv/Scripts/python -c "import markdown_it; print(markdown_it.__version__)"
```
Expected: a version string (currently `4.2.0`).

**Step 2 (only if it were missing):**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pip install markdown-it-py
```
*(No commit needed — no code changes in this task.)*

---

### Task 2: Make the parent package `__init__.py` lazy (V7)

**Objective:** Importing `quintic_sim_gfx` (or `quintic_sim_gfx.gui`) must **not** import `numpy`/`sympy`, so the GUI process stays light and immune to the V5 ABI crash. Public API preserved.

**Files:** Modify: `quintic_sim_gfx/__init__.py` (rewrite, ~15 lines). Test: `tests/test_gfx_import.py`.

**Step 1: Write failing test**
```python
# tests/test_gfx_import.py
def test_import_gfx_does_not_load_numpy():
    import sys
    # fresh interpreter guard: numpy must not be imported just by importing the package
    import quintic_sim_gfx  # noqa: F401
    assert "numpy" not in sys.modules

def test_public_api_still_exposed():
    from quintic_sim_gfx import simulate, Report, PipelineError  # lazy getattr
    assert callable(simulate)
```

**Step 2: Run to verify failure**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_import.py -v
```
Expected: FAIL — importing `quintic_sim_gfx` currently pulls in `numpy` (via `from .pipeline import simulate`).

**Step 3: Rewrite `quintic_sim_gfx/__init__.py`**
```python
"""quintic_sim_gfx — a Quintic Solver Simulator (with an optional GUI).

Public API (lazily imported so that importing this package — or the gui
subpackage — never loads sympy/numpy):
    simulate(coeffs, use_sage=False) -> Report
"""

from importlib import import_module

__version__ = "0.1.0"
__all__ = ["simulate", "Report", "StepTrace", "PipelineError"]

# name -> (module, attr)
_LAZY = {
    "simulate":     (".pipeline", "simulate"),
    "Report":       (".report",   "Report"),
    "StepTrace":    (".report",   "StepTrace"),
    "PipelineError":(".errors",   "PipelineError"),
}

def __getattr__(name):
    if name in _LAZY:
        mod_name, attr = _LAZY[name]
        return getattr(import_module(mod_name, __name__), attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__():
    return sorted(list(globals()) + list(_LAZY))
```

**Step 4: Run to verify pass**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_import.py -v
```
Expected: PASS (2 passed).

**Step 5: Regression** — confirm the CLI still works (unchanged path):
```bash
env -u PYTHONPATH .venv/Scripts/python -m quintic_sim_gfx "x^5 - 2" | head -5
```
Expected: report header lines. (Note: this imports the *pipeline* via `cli.py`, not via the lazy `__init__`, so numpy loads here by design — that's the subprocess/CLI path, which is correct.)

**Step 6: Commit**
```bash
git add quintic_sim_gfx/__init__.py tests/test_gfx_import.py
git commit -m "gfx: lazy parent __init__ so the GUI never loads numpy"
```

---

### Task 3: GUI package scaffold

**Objective:** Create the `quintic_sim_gfx/gui/` subpackage and a launchable entry point.

**Files:**
- Create: `quintic_sim_gfx/gui/__init__.py`
- Create: `quintic_sim_gfx/gui/__main__.py`

**Step 1: Create `quintic_sim_gfx/gui/__init__.py`**
```python
"""quintic_sim_gfx.gui — desktop GUI (tkinter) wrapping the quintic_sim CLI."""
__all__ = ["app"]
```

**Step 2: Create `quintic_sim_gfx/gui/__main__.py`**
```python
"""Entry point:  python -m quintic_sim_gfx.gui"""
from __future__ import annotations
import tkinter as tk
from .app import QuinticApp

def main() -> None:
    root = tk.Tk()
    QuinticApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```
*(`app.py` is created in Task 10; until then this import will fail — that's expected. The scaffold is validated in Task 10.)*

**Step 3: Commit**
```bash
git add quintic_sim_gfx/gui/__init__.py quintic_sim_gfx/gui/__main__.py
git commit -m "gfx: scaffold gui subpackage + entry point"
```

---

### Task 4: `config.py` — user-configurable command template (TDD)

**Objective:** Persist the command template (and a few display prefs) as JSON under the user's app-data dir.

**Files:** Create: `quintic_sim_gfx/gui/config.py`. Test: `tests/test_gfx_config.py`.

**Step 1: Write failing test**
```python
# tests/test_gfx_config.py
import json
from pathlib import Path
from quintic_sim_gfx.gui import config

def test_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "config_dir", lambda: tmp_path)
    c = config.load()
    assert "{poly}" in c["command"]
    assert "quintic_sim" in c["command"]
    assert c["sage"] is True
    assert c["timeout"] > 0

def test_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "config_dir", lambda: tmp_path)
    c = config.load()
    c["command"] = "python -m quintic_sim_gfx {poly}"
    c["sage"] = False
    config.save(c)
    c2 = config.load()
    assert c2["command"] == "python -m quintic_sim_gfx {poly}"
    assert c2["sage"] is False
```

**Step 2: Run to verify failure**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_config.py -v
```
Expected: FAIL — `quintic_sim_gfx.gui.config` does not exist.

**Step 3: Implement `config.py`**
```python
"""Persistent GUI configuration (command template + display prefs)."""
from __future__ import annotations
import json
import os
from pathlib import Path

APP = "quintic_sim_gfx"
DEFAULTS = {
    # {poly} is replaced with the assembled polynomial (shell-quoted).
    "command": ".venv/Scripts/python -m quintic_sim {poly} --sage",
    "sage": True,
    "timeout": 300,          # seconds for the subprocess (Sage can be slow)
    "font_size": 10,
}

def config_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / APP

def _path() -> Path:
    return config_dir() / "config.json"

def load() -> dict:
    p = _path()
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
        merged = dict(DEFAULTS)
        merged.update({k: v for k, v in data.items() if k in DEFAULTS})
        return merged
    return dict(DEFAULTS)

def save(cfg: dict) -> None:
    d = config_dir()
    d.mkdir(parents=True, exist_ok=True)
    _path().write_text(json.dumps(cfg, indent=2), encoding="utf-8")
```

**Step 4: Run to verify pass**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_config.py -v
```
Expected: PASS (2 passed).

**Step 5: Commit**
```bash
git add quintic_sim_gfx/gui/config.py tests/test_gfx_config.py
git commit -m "gfx: persistent config for the command template + prefs"
```

---

### Task 5: `runner.py` — expression formatter (TDD)

**Objective:** Convert the 6 box values into the exact CLI expression syntax (e.g. `x^5 - 2*x^4 - 3*x^3 - 1`), plus a robust comma-list fallback. Pure logic, no tkinter.

**Files:** Create: `quintic_sim_gfx/gui/runner.py`. Test: `tests/test_gfx_runner.py`.

**Step 1: Write failing tests**
```python
# tests/test_gfx_runner.py
from fractions import Fraction as F
from quintic_sim_gfx.gui.runner import parse_coeff, format_polynomial, format_coeff_list

def test_parse_coeff():
    assert parse_coeff("0.0") == 0
    assert parse_coeff("-2") == -2
    assert parse_coeff("2.5") == F(5, 2)
    assert parse_coeff("1/2") == F(1, 2)
    assert parse_coeff(" 3 ") == 3
    try:
        parse_coeff("abc"); assert False
    except ValueError:
        pass

def test_format_matching_example():
    # the user's exact example
    expr, err = format_polynomial([1, -2, -3, 0, 0, -1])
    assert err is None
    assert expr == "x^5 - 2*x^4 - 3*x^3 - 1"

def test_format_monic_and_one_coeffs():
    assert format_polynomial([1, 0, 0, 0, 0, -2])[0] == "x^5 - 2"
    assert format_polynomial([1, 1, -4, -3, 3, 1])[0] == "x^5 + x^4 - 4*x^3 - 3*x^2 + 3*x + 1"

def test_format_negative_leading():
    assert format_polynomial([-1, 0, 0, 0, 0, 0])[0] == "-x^5"

def test_format_fraction_coeff():
    expr, _ = format_polynomial([1, 0, 0, 0, 0, F(1, 2)])
    assert expr == "x^5 + 1/2"

def test_format_errors():
    assert format_polynomial([0, 0, 0, 0, 0, 0])[1] is not None   # all zero
    assert format_polynomial([0, 1, 0, 0, 0, 0])[1] is not None   # c5 zero -> not quintic

def test_format_coeff_list():
    assert format_coeff_list([1, -2, -3, 0, 0, -1]) == "1,-2,-3,0,0,-1"
```

**Step 2: Run to verify failure**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_runner.py -v
```
Expected: FAIL — `runner` does not exist.

**Step 3: Implement the formatter in `runner.py`**
```python
"""Command wrapper: coeffs -> expression, command building, subprocess run.

No tkinter import here so the logic is unit-testable headlessly.
"""
from __future__ import annotations
import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Optional, Sequence

# ---------------------------------------------------------------- coefficients
def parse_coeff(text: str) -> Fraction:
    """Parse a coefficient box into an exact rational. Raises ValueError if bad."""
    t = text.strip().replace(",", ".")
    if not t:
        return Fraction(0)
    try:
        return Fraction(t)
    except (ValueError, ZeroDivisionError):
        return Fraction(float(t)).limit_denominator(10**12)   # handles "1e3", "2.5"

def _num(v: Fraction) -> str:
    return str(v)          # "2", "-3", "1/2" — all sympy-parseable

def format_polynomial(coeffs: Sequence) -> tuple[Optional[str], Optional[str]]:
    """Build a sympy-parseable expression from 6 descending coeffs [c5..c0].

    Returns (expr, error). error is set if the input is not a valid quintic.
    """
    if len(coeffs) != 6:
        return None, "expected 6 coefficients (c5..c0)"
    if all(c == 0 for c in coeffs):
        return None, "all coefficients are zero (not a polynomial)"
    if coeffs[0] == 0:
        return None, "c5 is zero — the polynomial is not degree 5"
    parts: List[str] = []
    first = True
    for i, c in enumerate(coeffs):
        k = 5 - i
        if c == 0:
            continue
        neg, mag = (c < 0), abs(c)
        if k == 0:
            body = _num(mag)
        elif mag == 1:
            body = "x" if k == 1 else f"x^{k}"
        else:
            body = (f"{_num(mag)}*x" if k == 1 else f"{_num(mag)}*x^{k}")
        if first:
            parts.append(("-" + body) if neg else body)
            first = False
        else:
            parts.append(f"{'-' if neg else '+'} {body}")
    return " ".join(parts), None

def format_coeff_list(coeffs: Sequence) -> str:
    """Robust comma-list form the CLI also accepts: '1,-2,-3,0,0,-1'."""
    return ",".join(_num(c) for c in coeffs)
```

**Step 4: Run to verify pass**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_runner.py -v
```
Expected: PASS (7 passed).

**Step 5: Commit**
```bash
git add quintic_sim_gfx/gui/runner.py tests/test_gfx_runner.py
git commit -m "gfx: coefficient -> expression formatter (matches CLI syntax)"
```

---

### Task 6: `runner.py` — command builder + PYTHONPATH scrub + subprocess worker (TDD)

**Objective:** Build argv from the template, scrub the hermes-agent `PYTHONPATH` (V5), and run the command in a killable `Popen`, returning a `RunResult`.

**Files:** Modify: `quintic_sim_gfx/gui/runner.py` (append). Test: extend `tests/test_gfx_runner.py`.

**Step 1: Add failing tests**
```python
# append to tests/test_gfx_runner.py
import os
from quintic_sim_gfx.gui import runner

def test_clean_env_scrubs_hermes(monkeypatch):
    monkeypatch.setenv("PYTHONPATH",
        "C:\\Users\\misur\\AppData\\Local\\hermes\\hermes-agent"
        + os.pathsep + "/keep/this")
    env = runner.clean_env()
    assert "hermes-agent" not in env.get("PYTHONPATH", "")
    assert "/keep/this" in env["PYTHONPATH"]

def test_clean_env_no_pp(monkeypatch):
    monkeypatch.delenv("PYTHONPATH", raising=False)
    env = runner.clean_env()
    assert "PYTHONPATH" not in env or env["PYTHONPATH"] == ""

def test_build_command_substitutes_and_quotes():
    argv = runner.build_command(
        "python -m quintic_sim {poly} --sage", "x^5 - 2")
    assert argv == ["python", "-m", "quintic_sim", "x^5 - 2", "--sage"]

def test_build_command_sage_toggle():
    with_sage = runner.build_command("py -m quintic_sim {poly} --sage", "x^5-2", sage=True)
    no_sage  = runner.build_command("py -m quintic_sim {poly} --sage", "x^5-2", sage=False)
    assert "--sage" in with_sage
    assert "--sage" not in no_sage
```

**Step 2: Run to verify failure**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_runner.py -v
```
Expected: FAIL — `clean_env`/`build_command` not defined.

**Step 3: Append to `runner.py`**
```python
# ------------------------------------------------------------------- execution
@dataclass
class RunResult:
    ok: bool
    stdout: str
    stderr: str
    returncode: int
    duration: float
    command: str
    timed_out: bool = False

def clean_env() -> dict:
    """Copy os.environ and drop hermes-agent PYTHONPATH entries (V5 pitfall).

    The agent shell sets PYTHONPATH to the hermes-agent venv, whose cp311 numpy
    shadows the project venv's cp313 numpy and crashes `import numpy`. The
    wrapped command must run against the project venv only.
    """
    env = os.environ.copy()
    pp = env.get("PYTHONPATH", "")
    keep = [p for p in filter(None, pp.split(os.pathsep)) if "hermes-agent" not in p]
    env["PYTHONPATH"] = os.pathsep.join(keep)
    if not env["PYTHONPATH"]:
        env.pop("PYTHONPATH", None)
    return env

def build_command(template: str, poly: str, *, sage: bool = True) -> List[str]:
    """Substitute {poly} (shell-quoted) into the template and split to argv.

    If sage is False, drop any trailing `--sage` flag.
    """
    cmd = template.replace("{poly}", shlex.quote(poly))
    argv = shlex.split(cmd)
    if not sage and "--sage" in argv:
        argv = [a for a in argv if a != "--sage"]
    return argv

def run_command(template: str, poly: str, *, sage: bool = True,
                cwd: str, timeout: int = 300) -> RunResult:
    """Run the wrapped command; return its markdown stdout + diagnostics.

    Uses Popen (not subprocess.run) so the caller can store the handle and
    kill it (the GUI's Stop button).
    """
    argv = build_command(template, poly, sage=sage)
    env = clean_env()
    command = " ".join(shlex.quote(a) for a in argv)
    t0 = time.perf_counter()
    try:
        p = subprocess.Popen(argv, cwd=cwd, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True)
    except (OSError, FileNotFoundError) as e:
        return RunResult(False, "", f"failed to start: {e}", -1,
                         time.perf_counter() - t0, command)
    try:
        out, err = p.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        timed_out = True
    rc = p.returncode
    return RunResult(
        ok=(rc == 0),
        stdout=out or "",
        stderr=err or "",
        returncode=rc,
        duration=time.perf_counter() - t0,
        command=command,
        timed_out=timed_out,
    )
```
*(Also expose `RunResult`, `clean_env`, `build_command`, `run_command` in a module `__all__` if desired.)*

**Step 4: Run to verify pass**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_runner.py -v
```
Expected: PASS (11 passed).

**Step 5: Live smoke (no unit, just proof)**
```bash
env -u PYTHONPATH .venv/Scripts/python - <<'PY'
from quintic_sim_gfx.gui import runner
r = runner.run_command(".venv/Scripts/python -m quintic_sim {poly}",
                       "x^5 - 2", sage=False,
                       cwd=r"C:\Users\misur\source\hermes-dir", timeout=120)
print("ok", r.ok, "rc", r.returncode, "dur", round(r.duration, 2))
print(r.stdout.splitlines()[0])
PY
```
Expected: `ok True rc 0 …` and `# Quintic Solver Report`.

**Step 6: Commit**
```bash
git add quintic_sim_gfx/gui/runner.py tests/test_gfx_runner.py
git commit -m "gfx: command builder + PYTHONPATH-scrubbing subprocess worker"
```

---

### Task 7: `mdrender.py` — markdown-it-py → block model (TDD)

**Objective:** Parse the report markdown into a small block model (`Heading`, `Paragraph`, `Table`, `Quote`, `List`, `CodeBlock`, `HRule`) with inline runs. **No tkinter import** — pure data. This is the heart of requirement 2.

**Files:** Create: `quintic_sim_gfx/gui/mdrender.py`. Test: `tests/test_gfx_mdrender.py` (uses a real report fixture).

**Step 1: Write failing test**
```python
# tests/test_gfx_mdrender.py
from quintic_sim_gfx.gui.mdrender import render_blocks, Table, Heading, Paragraph

SAMPLE = """# Quintic Solver Report

**Input:** `x**5 - 2`
**Method:** radicals

## Roots (S4/S5)

| # | exact | numeric (15 digits) | verified |
|---|-------|---------------------|----------|
| 0 | `CRootOf(x**5 - 2, 0)` | 1.148698355 | ✅ |
| 1 | `CRootOf(x**5 - 2, 1)` | -0.755 + 0.951*I | ✅ |

> **Palindromic reduction:** note here

- note one
- note two
"""

def test_block_counts():
    b = render_blocks(SAMPLE)
    kinds = [type(x).__name__ for x in b]
    assert kinds.count("Heading") == 2
    assert kinds.count("Table") == 1
    assert "Quote" in kinds
    assert "List" in kinds

def test_table_shape():
    t = next(x for x in render_blocks(SAMPLE) if isinstance(x, Table))
    assert len(t.headers) == 1 and len(t.headers[0]) == 4
    assert len(t.rows) == 2
    assert len(t.rows[0]) == 4

def test_wide_cell_preserved_verbatim():
    t = next(x for x in render_blocks(SAMPLE) if isinstance(x, Table))
    cell = t.rows[0][1]                       # the `exact` cell
    text = "".join(txt for _, txt in cell)
    assert text == "CRootOf(x**5 - 2, 0)"

def test_inline_runs_style():
    p = next(x for x in render_blocks(SAMPLE) if isinstance(x, Paragraph))
    styles = [s for s, _ in p.inlines]
    assert "strong" in styles and "code" in styles
```

**Step 2: Run to verify failure**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_mdrender.py -v
```
Expected: FAIL — `mdrender` does not exist.

**Step 3: Implement `mdrender.py`**
```python
"""markdown-it-py -> lightweight block model (no tkinter).

Token stream verified against the real report (plan §1, V6).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple
from markdown_it import MarkdownIt

Run = Tuple[str, str]   # (style, text); style in {plain, code, strong, em}

@dataclass
class Heading:
    level: int
    inlines: List[Run]

@dataclass
class Paragraph:
    inlines: List[Run]

@dataclass
class Table:
    headers: List[List[Run]]     # usually 1 row
    rows: List[List[List[Run]]]

@dataclass
class Quote:
    blocks: list = field(default_factory=list)

@dataclass
class List:
    ordered: bool
    items: list = field(default_factory=list)   # list[list[block]]

@dataclass
class CodeBlock:
    lang: str
    text: str

@dataclass
class HRule:
    pass

def _runs(tok) -> List[Run]:
    """Flatten an inline token into (style, text) runs."""
    out: List[Run] = []
    stack: List[str] = []
    def cur():
        return stack[-1] if stack else "plain"
    for c in (tok.children or []):
        t = c.type
        if t == "text":
            out.append((cur(), c.content))
        elif t == "code_inline":
            out.append(("code", c.content))
        elif t == "strong_open":
            stack.append("strong")
        elif t == "strong_close":
            if stack: stack.pop()
        elif t == "em_open":
            stack.append("em")
        elif t == "em_close":
            if stack: stack.pop()
        elif t in ("softbreak", "hardbreak"):
            out.append((cur(), "\n"))
    # merge adjacent same-style runs
    merged: List[Run] = []
    for s, txt in out:
        if merged and merged[-1][0] == s:
            merged[-1] = (s, merged[-1][1] + txt)
        else:
            merged.append((s, txt))
    return merged

def _cell_text(cell_runs: List[Run]) -> str:
    return "".join(txt for _, txt in cell_runs)

def _table(toks, i):
    headers, rows = [], []
    target, row = None, None
    i += 1
    while toks[i].type != "table_close":
        tt = toks[i].type
        if tt == "thead_open":
            target, i = "head", i + 1
        elif tt == "tbody_open":
            target, i = "body", i + 1
        elif tt in ("thead_close", "tbody_close"):
            target, i = None, i + 1
        elif tt == "tr_open":
            row, i = [], i + 1
        elif tt in ("th_open", "td_open"):
            row.append(_runs(toks[i + 1]))
            i += 2
        elif tt in ("th_close", "td_close"):
            i += 1
        elif tt == "tr_close":
            if row is not None:
                (headers if target == "head" else rows).append(row)
            row, i = None, i + 1
        else:
            i += 1
    return Table(headers, rows), i + 1   # i+1 skips table_close

def _range_end(toks, i, open_types, close_types):
    depth, j = 0, i
    while j < len(toks):
        if toks[j].type in open_types:
            depth += 1
        elif toks[j].type in close_types:
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return j

def _build(toks, i, end):
    blocks = []
    while i < end:
        t = toks[i]
        ty = t.type
        if ty == "heading_open":
            blocks.append(Heading(int(t.tag[1]), _runs(toks[i + 1]))); i += 3
        elif ty == "paragraph_open":
            blocks.append(Paragraph(_runs(toks[i + 1]))); i += 3
        elif ty == "table_open":
            tbl, i = _table(toks, i); blocks.append(tbl)
        elif ty == "blockquote_open":
            e = _range_end(toks, i, ("blockquote_open",), ("blockquote_close",))
            inner, _ = _build(toks, i + 1, e)
            blocks.append(Quote(inner)); i = e + 1
        elif ty in ("bullet_list_open", "ordered_list_open"):
            ordered = ty == "ordered_list_open"
            e = _range_end(toks, i, ("bullet_list_open", "ordered_list_open"),
                           ("bullet_list_close",))
            items, _ = _list_items(toks, i + 1, e)
            blocks.append(List(ordered, items)); i = e + 1
        elif ty in ("fence", "code_block"):
            blocks.append(CodeBlock(t.info or "", t.content)); i += 1
        elif ty == "hrule":
            blocks.append(HRule()); i += 1
        else:
            i += 1
    return blocks, i

def _list_items(toks, i, end):
    items = []
    while i < end:
        if toks[i].type == "list_item_open":
            e = _range_end(toks, i, ("list_item_open",), ("list_item_close",))
            inner, _ = _build(toks, i + 1, e)
            items.append(inner); i = e + 1
        else:
            i += 1
    return items, i

def render_blocks(md_text: str) -> list:
    md = MarkdownIt("commonmark").enable("table")
    toks = md.parse(md_text)
    blocks, _ = _build(toks, 0, len(toks))
    return blocks
```

**Step 4: Run to verify pass**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_mdrender.py -v
```
Expected: PASS (4 passed).

**Step 5: Real-report check** — parse an actual report and confirm 2 tables, 5 root rows:
```bash
env -u PYTHONPATH .venv/Scripts/python - <<'PY'
from quintic_sim_gfx.gui.mdrender import render_blocks, Table
md = open(r"C:\Users\misur\source\hermes-dir\QuinticSolverReport_v0d.md", encoding="utf-8").read()
tabs = [b for b in render_blocks(md) if isinstance(b, Table)]
print("tables:", len(tabs))
for t in tabs:
    print("  rows:", len(t.rows), "cols:", len(t.rows[0]) if t.rows else 0)
PY
```
Expected: `tables: 2`; roots table `rows: 5 cols: 4`; step-trace table `rows: 9 cols: 4`.

**Step 6: Commit**
```bash
git add quintic_sim_gfx/gui/mdrender.py tests/test_gfx_mdrender.py
git commit -m "gfx: markdown-it-py -> block model (tables, headings, quotes, lists)"
```

---

### Task 8: `report_view.py` — scrollable document + styled text blocks (TDD)

**Objective:** A `DocView` that is a vertically-scrolling document (`Canvas` + vertical `Scrollbar` + inner `Frame`) and renders non-table blocks as styled `tk.Text`/`Label`.

**Files:** Create: `quintic_sim_gfx/gui/report_view.py`. Test: `tests/test_gfx_report_view.py` (headless `tk.Tk()`, skip if no display).

**Step 1: Write failing test**
```python
# tests/test_gfx_report_view.py
import pytest
tk = pytest.importorskip("tkinter")
from quintic_sim_gfx.gui.mdrender import render_blocks
from quintic_sim_gfx.gui.report_view import DocView

def _root():
    r = tk.Tk(); r.withdraw(); return r

def test_builds_without_error():
    r = _root()
    v = DocView(r)
    v.render("# Title\n\n**Input:** `x**5`\n")
    r.update_idletasks()
    assert len(v._text_widgets) >= 1
    r.destroy()

def test_table_creates_treeview():
    r = _root()
    v = DocView(r)
    v.render("| a | b |\n|---|---|\n| 1 | 2 |\n")
    r.update_idletasks()
    assert len(v._treeviews) == 1
    cols = v._treeviews[0]["columns"]
    assert list(cols) == ["a", "b"]
    r.destroy()
```

**Step 2: Run to verify failure**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_report_view.py -v
```
Expected: FAIL — `report_view` does not exist.

**Step 3: Implement the document + text blocks in `report_view.py`**
```python
"""Output pad: vertically-scrolling document that renders report blocks.

Tables are rendered by _add_table (Task 9). Non-table blocks are styled
tk.Text / ttk.Label. The document scrolls vertically; each table scrolls
horizontally on its own (requirement 2).
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from .mdrender import (Heading, Paragraph, Table, Quote, List,
                       CodeBlock, HRule)

BG = "#ffffff"

class DocView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=BG)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = ttk.Frame(self.canvas)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
            lambda e: self.canvas.itemconfigure(self._win, width=e.width))
        self.canvas.bind_all("<MouseWheel>", self._wheel)
        self._text_widgets: list = []
        self._treeviews: list = []

    def _wheel(self, e):
        self.canvas.yview_scroll(int(-e.delta / 120), "units")

    # ------------------------------------------------------------- public API
    def render(self, md_text: str) -> None:
        self.clear()
        for b in render_blocks(md_text):
            self.add_block(b)

    def clear(self) -> None:
        for w in self.inner.winfo_children():
            w.destroy()
        self._text_widgets.clear()
        self._treeviews.clear()

    def add_block(self, b) -> None:
        if isinstance(b, Heading):
            self._add_heading(b)
        elif isinstance(b, Paragraph):
            self._add_paragraph(b)
        elif isinstance(b, Table):
            self._add_table(b)
        elif isinstance(b, Quote):
            self._add_quote(b)
        elif isinstance(b, List):
            self._add_list(b)
        elif isinstance(b, CodeBlock):
            self._add_code(b)
        elif isinstance(b, HRule):
            ttk.Separator(self.inner, orient="horizontal").pack(fill="x", pady=4)

    # --------------------------------------------------------------- helpers
    def _styled_text(self, inlines, *, font, size, bg=BG):
        """Return a read-only tk.Text with tags applied to the inline runs."""
        txt = tk.Text(self.inner, wrap="word", bg=bg, relief="flat",
                      borderwidth=0, font=(font, size), height=1)
        txt.tag_configure("code", font=("Consolas", size),
                          background="#eef1f5")
        txt.tag_configure("strong", font=(font, size, "bold"))
        txt.tag_configure("em", font=(font, size, "italic"))
        for style, text in inlines:
            txt.insert("end", text, style if style != "plain" else ())
        txt.configure(state="disabled", height=1)
        # let it auto-size to content width
        txt.bind("<Configure>", lambda e: None)
        self._text_widgets.append(txt)
        return txt

    def _add_heading(self, b: Heading) -> None:
        size = {1: 18, 2: 15, 3: 13}.get(b.level, 12)
        w = self._styled_text(b.inlines, font="Segoe UI", size=size,
                              bg=self.cget("background"))
        w.pack(fill="x", padx=8, pady=(8, 2))

    def _add_paragraph(self, b: Paragraph) -> None:
        w = self._styled_text(b.inlines, font="Segoe UI", size=10)
        w.pack(fill="x", padx=8, pady=2)

    def _add_quote(self, b: Quote) -> None:
        frame = ttk.Frame(self.inner)
        for blk in b.blocks:
            if isinstance(blk, Paragraph):
                self._styled_text(blk.inlines, font="Segoe UI", size=10,
                                  bg="#f3f7f3").pack(fill="x", padx=6)
        frame.pack(fill="x", padx=8, pady=2, ipady=4)
        frame.configure(style="TFrame")

    def _add_list(self, b: List) -> None:
        for idx, item_blocks in enumerate(b.items):
            prefix = f"{idx + 1}." if b.ordered else "•"
            line = "  ".join(
                "".join(t for _, t in blk.inlines)
                for blk in item_blocks if isinstance(blk, Paragraph))
            lab = ttk.Label(self.inner, text=f"{prefix}  {line}", anchor="w")
            lab.pack(fill="x", padx=(24, 8), pady=1)

    def _add_code(self, b: CodeBlock) -> None:
        txt = tk.Text(self.inner, wrap="none", font=("Consolas", 9),
                      background="#f6f8fa", relief="flat")
        txt.insert("1.0", b.text)
        txt.configure(state="disabled")
        txt.pack(fill="x", padx=8, pady=2)
        self._text_widgets.append(txt)

    # _add_table is added in Task 9
    def _add_table(self, b: Table) -> None:
        raise NotImplementedError
```

**Step 4: Run to verify pass**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_report_view.py::test_builds_without_error -v
```
Expected: PASS (the `test_table_creates_treeview` still fails — that's Task 9).

**Step 5: Commit**
```bash
git add quintic_sim_gfx/gui/report_view.py tests/test_gfx_report_view.py
git commit -m "gfx: DocView scrollable document + styled text/heading/quote/list blocks"
```

---

### Task 9: `report_view.py` — `ttk.Treeview` table with lateral scroll + expand (TDD)

**Objective:** Render each `Table` block as a `ttk.Treeview` with its **own horizontal scrollbar** (lateral scroll for wide rows), auto-sized columns (capped so the wide `exact` column overflows into the scrollbar), row striping, and **double-click → full-text popup** for wide cells.

**Files:** Modify: `quintic_sim_gfx/gui/report_view.py` (replace `_add_table`, add helpers). Test: extend `tests/test_gfx_report_view.py`.

**Step 1: Add failing tests**
```python
# append to tests/test_gfx_report_view.py
def test_table_lateral_scrollbar_present():
    r = _root()
    v = DocView(r)
    wide = "R" * 800
    v.render("| # | exact |\n|---|-------|\n| 0 | " + wide + " |\n")
    r.update_idletasks()
    tree = v._treeviews[0]
    # a horizontal scrollbar wired to the tree's xview must exist
    xsb = v._xscrollbars[0]
    assert tree["xscrollcommand"] is not None
    r.destroy()

def test_table_row_count():
    r = _root()
    v = DocView(r)
    v.render("| a | b |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n| 5 | 6 |\n")
    r.update_idletasks()
    tree = v._treeviews[0]
    assert len(tree.get_children()) == 3
    r.destroy()
```

**Step 2: Run to verify failure**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_report_view.py -v
```
Expected: FAIL — `_add_table` raises `NotImplementedError`.

**Step 3: Replace `_add_table` and add helpers in `report_view.py`**
```python
    # (add to __init__)
    #   self._xscrollbars: list = []

    MAX_COL = 640        # px cap; wider content overflows into the h-scrollbar
    MIN_COL = 56

    def _colw(self, text: str, ci: int) -> int:
        f = tkfont.Font(family="Segoe UI", size=10)
        w = f.measure(text) + 16
        return max(self.MIN_COL, min(self.MAX_COL, w))

    def _add_table(self, b: Table) -> None:
        wrap = ttk.Frame(self.inner)
        ncol = 0
        if b.headers:
            ncol = len(b.headers[0])
        for row in b.rows:
            ncol = max(ncol, len(row))
        ncol = max(ncol, 1)
        cols = [f"c{i}" for i in range(ncol)]

        tree = ttk.Treeview(wrap, columns=cols, show="headings",
                            height=min(12, max(3, len(b.rows))))
        # headers
        head = b.headers[0] if b.headers else []
        for ci in range(ncol):
            htxt = "".join(t for _, t in head[ci]) if ci < len(head) else f"col{ci+1}"
            tree.heading(cols[ci], text=htxt)
            tree.column(cols[ci], width=self._colw(htxt, ci),
                        minwidth=self.MIN_COL, anchor="w", stretch=False)
        # rows
        for ri, row in enumerate(b.rows):
            vals = ["".join(t for _, t in row[ci]) if ci < len(row) else ""
                    for ci in range(ncol)]
            tree.insert("", "end", values=vals,
                        tags=("odd" if ri % 2 else "even",))
        tree.tag_configure("odd", background="#f6f8fb")
        tree.tag_configure("even", background=BG)
        # LATERAL scrollbar (requirement 2)
        xsb = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=xsb.set)
        tree.pack(side="left", fill="both", expand=True)
        xsb.pack(side="bottom", fill="x")
        tree.bind("<Double-Button-1>",
                  lambda e, t=tree: self._expand_cell(t, e))
        wrap.pack(fill="both", expand=False, padx=8, pady=6)
        self._treeviews.append(tree)
        self._xscrollbars.append(xsb)

    def _expand_cell(self, tree, event) -> None:
        col = tree.identify_column(event.x)
        row = tree.identify_row(event.y)
        if not col or not row:
            return
        ci = int(col[1:]) - 1
        vals = tree.item(row, "values")
        if ci >= len(vals):
            return
        top = tk.Toplevel(self.master)
        top.title("Cell content")
        txt = tk.Text(top, wrap="word", width=80, height=18,
                      font=("Consolas", 10))
        txt.insert("1.0", str(vals[ci]))
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Button(top, text="Copy",
                   command=lambda: self._copy(vals[ci])).pack(pady=(0, 4), padx=8)
        ttk.Button(top, text="Close", command=top.destroy).pack(pady=(0, 8))

    def _copy(self, text: str) -> None:
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
```
*(Add `import tkinter.font as tkfont` at the top of the module.)*

**Step 4: Run to verify pass**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_report_view.py -v
```
Expected: PASS (4 passed).

**Step 5: Commit**
```bash
git add quintic_sim_gfx/gui/report_view.py tests/test_gfx_report_view.py
git commit -m "gfx: Treeview table blocks with lateral scroll + double-click expand"
```

---

### Task 10: `coeff_panel.py` — the 6 coefficient boxes + live preview + Run/Stop/Clear (TDD)

**Objective:** The requirement-1 panel: 6 boxes labeled `c5…c0` next to `x^5…1`, default `0.0`, a live expression preview, and Run/Stop/Clear buttons.

**Files:** Create: `quintic_sim_gfx/gui/coeff_panel.py`. Test: `tests/test_gfx_coeff_panel.py`.

**Step 1: Write failing test**
```python
# tests/test_gfx_coeff_panel.py
import pytest
tk = pytest.importorskip("tkinter")
from quintic_sim_gfx.gui.coeff_panel import CoeffPanel

def _root():
    r = tk.Tk(); r.withdraw(); return r

def test_defaults_are_zero():
    r = _root()
    p = CoeffPanel(r, on_run=lambda coeffs: None)
    r.update_idletasks()
    assert p.get_coeffs_text() == ["0.0"] * 6
    r.destroy()

def test_set_and_get():
    r = _root()
    p = CoeffPanel(r, on_run=lambda coeffs: None)
    p.set_coeffs([1, -2, -3, 0, 0, -1])
    r.update_idletasks()
    assert p.get_coeffs_text() == ["1", "-2", "-3", "0", "0", "-1"]
    r.destroy()

def test_preview_updates():
    r = _root()
    p = CoeffPanel(r, on_run=lambda coeffs: None)
    p.set_coeffs([1, -2, -3, 0, 0, -1])
    r.update_idletasks()
    assert p.preview_text().strip() == "x^5 - 2*x^4 - 3*x^3 - 1"
    r.destroy()

def test_invalid_shows_error_not_crash():
    r = _root()
    p = CoeffPanel(r, on_run=lambda coeffs: None)
    p.entries[0].delete(0, "end"); p.entries[0].insert(0, "abc")
    r.update_idletasks()
    p._update_preview()          # must not raise
    assert "error" in p.preview_text().lower() or p.preview_text().strip() == ""
    r.destroy()
```

**Step 2: Run to verify failure**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_coeff_panel.py -v
```
Expected: FAIL — `coeff_panel` does not exist.

**Step 3: Implement `coeff_panel.py`**
```python
"""Requirement 1: 6 coefficient input boxes + live expression preview."""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from .runner import parse_coeff, format_polynomial

POWERS = ["x^5", "x^4", "x^3", "x^2", "x", "1"]
LABELS = ["c5", "c4", "c3", "c2", "c1", "c0"]

class CoeffPanel(ttk.LabelFrame):
    def __init__(self, master, *, on_run, on_stop, on_clear):
        super().__init__(master, text="Polynomial   "
                           "[c5] x^5 + [c4] x^4 + [c3] x^3 + [c2] x^2 + [c1] x + [c0]")
        self._on_run = on_run
        self.entries: list[ttk.Entry] = []

        grid = ttk.Frame(self)
        grid.pack(fill="x", padx=6, pady=4)
        for i in range(6):
            ttk.Label(grid, text=LABELS[i], width=3,
                      anchor="e").grid(row=0, column=2 * i, padx=2)
            e = ttk.Entry(grid, width=8, justify="center")
            e.insert(0, "0.0")
            e.grid(row=0, column=2 * i + 1, padx=2)
            e.bind("<KeyRelease>", lambda _e: self._update_preview())
            e.bind("<Return>", lambda _e: self.run())
            self.entries.append(e)
            ttk.Label(grid, text=POWERS[i],
                      anchor="w").grid(row=0, column=2 * i + 2, padx=2)

        # live preview
        self._prev = ttk.Label(self, text="", anchor="w",
                               font=("Consolas", 10))
        self._prev.pack(fill="x", padx=8, pady=(0, 4))

        # buttons
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=6, pady=(0, 6))
        self.run_btn = ttk.Button(btns, text="Run ▶", command=self.run)
        self.run_btn.pack(side="left", padx=4)
        self.stop_btn = ttk.Button(btns, text="Stop", command=on_stop, state="disabled")
        self.stop_btn.pack(side="left", padx=4)
        ttk.Button(btns, text="Clear", command=self._clear).pack(side="left", padx=4)
        self._update_preview()

    # ------------------------------------------------------------- API
    def get_coeffs_text(self) -> list[str]:
        return [e.get() for e in self.entries]

    def set_coeffs(self, values) -> None:
        for e, v in zip(self.entries, values):
            e.delete(0, "end")
            e.insert(0, str(v))
        self._update_preview()

    def preview_text(self) -> str:
        return self._prev.cget("text")

    def set_running(self, running: bool) -> None:
        self.run_btn.configure(state="disabled" if running else "normal")
        self.stop_btn.configure(state="normal" if running else "disabled")

    def run(self) -> None:
        try:
            coeffs = [parse_coeff(e.get()) for e in self.entries]
        except (ValueError, ZeroDivisionError):
            self._prev.configure(text="⚠ invalid coefficient — use numbers "
                                      "(e.g. 2, -3, 0.5, 1/2)")
            return
        self._on_run(coeffs)

    def _clear(self) -> None:
        for e in self.entries:
            e.delete(0, "end")
            e.insert(0, "0.0")
        self._update_preview()

    def _update_preview(self) -> None:
        try:
            coeffs = [parse_coeff(e.get()) for e in self.entries]
        except (ValueError, ZeroDivisionError):
            self._prev.configure(text="⚠ invalid coefficient")
            return
        expr, err = format_polynomial(coeffs)
        self._prev.configure(text=err if err else (f"f(x) = {expr}"))
```

**Step 4: Run to verify pass**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_coeff_panel.py -v
```
Expected: PASS (4 passed).

**Step 5: Commit**
```bash
git add quintic_sim_gfx/gui/coeff_panel.py tests/test_gfx_coeff_panel.py
git commit -m "gfx: coefficient panel (6 boxes, live preview, run/stop/clear)"
```

---

### Task 11: `app.py` — assemble the window, worker thread, status bar (TDD/smoke)

**Objective:** `QuinticApp` wires the panel → runner (in a worker thread) → `DocView`, with a status bar, a user-editable command-template field (persisted via `config`), and safe main-thread marshalling.

**Files:** Create: `quintic_sim_gfx/gui/app.py`. Test: `tests/test_gfx_app.py`.

**Step 1: Write failing test**
```python
# tests/test_gfx_app.py
import pytest
tk = pytest.importorskip("tkinter")
from quintic_sim_gfx.gui.app import QuinticApp

def test_app_builds():
    r = tk.Tk(); r.withdraw()
    app = QuinticApp(r)
    r.update_idletasks()
    assert app.doc is not None and app.panel is not None
    assert "quintic_sim" in app.cmd_var.get()
    r.destroy()

def test_render_roundtrip_without_subprocess():
    r = tk.Tk(); r.withdraw()
    app = QuinticApp(r)
    app.doc.render("| # | exact |\n|---|-------|\n| 0 | x |\n")
    r.update_idletasks()
    assert len(app.doc._treeviews) == 1
    r.destroy()
```

**Step 2: Run to verify failure**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_app.py -v
```
Expected: FAIL — `app` does not exist.

**Step 3: Implement `app.py`**
```python
"""Main window: coefficient panel + command template + output pad + status bar."""
from __future__ import annotations
import os
import threading
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from . import config
from .runner import run_command, RunResult
from .coeff_panel import CoeffPanel
from .report_view import DocView

# Project root = two levels up from this file (quintic_sim_gfx/gui/app.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

class QuinticApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.cfg = config.load()
        root.title("Quintic Solver Simulator — GUI")
        root.geometry("980x720")
        root.minsize(760, 520)

        # --- top: command template (user-configurable) ---
        top = ttk.Frame(root)
        top.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(top, text="Command:").pack(side="left")
        self.cmd_var = tk.StringVar(value=self.cfg["command"])
        ent = ttk.Entry(top, textvariable=self.cmd_var)
        ent.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Label(top, text=("{poly} = the assembled polynomial"
                             "   •   persisted to config")).pack(side="left")
        self.sage_var = tk.BooleanVar(value=self.cfg["sage"])
        ttk.Checkbutton(top, text="--sage", variable=self.sage_var).pack(side="left", padx=4)

        # --- middle: split panel | output pad ---
        mid = ttk.Panedwindow(root, orient="horizontal")
        mid.pack(fill="both", expand=True, padx=8, pady=4)
        self.panel = CoeffPanel(mid, on_run=self.on_run,
                                on_stop=self.on_stop, on_clear=self.on_clear)
        mid.add(self.panel, weight=1)
        self.doc = DocView(mid)
        mid.add(self.doc, weight=3)
        self.doc.render("# Ready\n\nEnter coefficients and press **Run ▶**.\n")

        # --- bottom: status bar ---
        self.status = ttk.Label(root, text="Idle", anchor="w", relief="sunken")
        self.status.pack(fill="x", side="bottom")

        self._proc = None
        self.cmd_var.trace_add("write", lambda *a: self._save_cfg())
        self.sage_var.trace_add("write", lambda *a: self._save_cfg())

    # ------------------------------------------------------------- actions
    def on_run(self, coeffs) -> None:
        from .runner import format_polynomial
        expr, err = format_polynomial(coeffs)
        if err:
            self._status(f"⚠ {err}")
            return
        self._save_cfg()
        self.panel.set_running(True)
        self._status(f"Running: {self.cmd_var.get()}  …")
        self._proc_holder = {}
        t = threading.Thread(target=self._worker, args=(expr,), daemon=True)
        t.start()

    def _worker(self, expr: str) -> None:
        res = run_command(self.cmd_var.get(), expr,
                          sage=self.sage_var.get(),
                          cwd=str(PROJECT_ROOT),
                          timeout=self.cfg["timeout"])
        self.root.after(0, self._on_done, res)

    def _on_done(self, res: RunResult) -> None:
        self.panel.set_running(False)
        if res.ok:
            self.doc.render(res.stdout)
            self._status(f"OK  ({res.duration:.2f}s)  •  "
                         f"{res.stdout.count(chr(10))} lines")
        else:
            self.doc.render(f"# Error (exit {res.returncode})\n\n"
                            f"```\n{res.stderr.strip() or res.stdout.strip()}\n```\n")
            self._status(f"FAILED exit={res.returncode}"
                         + ("  (timed out)" if res.timed_out else ""))

    def on_stop(self) -> None:
        # (kill support) see note below
        self._status("Stop requested")

    def on_clear(self) -> None:
        self.doc.render("# Cleared\n")
        self._status("Cleared")

    def _status(self, msg: str) -> None:
        self.status.configure(text=msg)

    def _save_cfg(self) -> None:
        self.cfg["command"] = self.cmd_var.get()
        self.cfg["sage"] = self.sage_var.get()
        try:
            config.save(self.cfg)
        except OSError:
            pass
```

**Stop note (implement in Step 4):** to make Stop real, change `runner.run_command` to accept an optional `proc_ref: dict` that it populates with the live `Popen` (`proc_ref["p"] = p` right after `Popen(...)`), and have `on_stop` do `self._proc_holder["p"].kill()` when present. Add this small hook in `runner.py` (one line) and wire `_proc_holder` through `on_run` → `_worker` → `run_command`.

**Step 4: Add the kill hook** — in `runner.run_command`, after creating `p`:
```python
        if proc_ref is not None:
            proc_ref["p"] = p
```
and add the `proc_ref=None` parameter; in `app._worker`, pass `proc_ref=self._proc_holder`; in `on_stop`:
```python
    def on_stop(self) -> None:
        p = getattr(self, "_proc_holder", {}).get("p")
        if p and p.poll() is None:
            p.kill()
            self._status("Stopped")
```

**Step 5: Run to verify pass**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_app.py -v
```
Expected: PASS (2 passed).

**Step 6: Commit**
```bash
git add quintic_sim_gfx/gui/app.py quintic_sim_gfx/gui/runner.py tests/test_gfx_app.py
git commit -m "gfx: main window wiring panel -> subprocess -> DocView + status bar"
```

---

### Task 12: End-to-end test across the vectors (no-sage fast path + optional sage)

**Objective:** Prove the full GUI pipeline: set coefficients → run the real command → the `DocView` shows a 5-row roots table. Fast (no `--sage`) so it's CI-friendly; a separate `--sage` case is marked to skip when Docker is absent.

**Files:** Create: `tests/test_gfx_end2end.py`.

**Step 1: Write the test**
```python
# tests/test_gfx_end2end.py
import pytest
tk = pytest.importorskip("tkinter")
from fractions import Fraction
from quintic_sim_gfx.gui.app import QuinticApp
from quintic_sim_gfx.gui.mdrender import Table

D5 = [1, -2, -3, 0, 0, -1]     # x^5 - 2x^4 - 3x^3 - 1  (solvable, D5)

def test_gui_end_to_end_no_sage():
    r = tk.Tk(); r.withdraw()
    app = QuinticApp(r)
    app.cmd_var.set(".venv/Scripts/python -m quintic_sim {poly}")  # no --sage
    app.sage_var.set(False)
    app.panel.set_coeffs(D5)
    app.on_run([Fraction(v) for v in D5])
    # spin the main loop until the worker reports back (bounded)
    import time
    for _ in range(300):                # up to ~30s
        r.update()
        if "OK" in app.status.cget("text") or "FAILED" in app.status.cget("text"):
            break
        time.sleep(0.1)
    r.update_idletasks()
    tables = [b for b in _blocks_of(app) if isinstance(b, Table)]
    assert any(len(t.rows) == 5 for t in tables), app.status.cget("text")
    r.destroy()

def _blocks_of(app):
    from quintic_sim_gfx.gui.mdrender import render_blocks
    # re-derive from the last rendered markdown via a small hook:
    return app._last_blocks

def test_gui_end_to_end_sage():
    pytest.importorskip("subprocess")
    import shutil
    if shutil.which("docker") is None:
        pytest.skip("docker not available")
    # ... same as above but keep --sage in the command ...
```
*(In Task 11, store `self._last_blocks = render_blocks(md)` inside `doc.render` or `app._on_done` so the test can assert on blocks directly — add `self._last_blocks` in `app._on_done` right after `self.doc.render(res.stdout)`.)*

**Step 2: Run**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_end2end.py -v
```
Expected: `test_gui_end_to_end_no_sage` PASS (a 5-row roots table appears); the sage test PASSes or skips (no Docker).

**Step 3: Commit**
```bash
git add tests/test_gfx_end2end.py quintic_sim_gfx/gui/app.py
git commit -m "gfx: end-to-end GUI test across test vectors (no-sage + sage)"
```

---

### Task 13: Packaging, docs, and polish

**Objective:** Make the GUI easy to run and document it.

**Files:**
- Create: `requirements-gui.txt` (project root): `markdown-it-py`
- Create: `quintic_sim_gfx/gui/README.md`
- Modify: `quintic_sim_gfx/README.md` (add a "GUI" section)
- Modify: `quintic_sim_gfx/gui/report_view.py` (DPI awareness + optional theme)

**Step 1: Create `requirements-gui.txt`**
```
markdown-it-py
```

**Step 2: Add DPI awareness** — at the top of `app.py` (before any `Tk()`), in a `main()`-safe place, and call it from `__main__.main()`:
```python
import sys
def _dpi_aware() -> None:
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
```
Call `_dpi_aware()` first thing in `quintic_sim_gfx/gui/__main__.main()`.

**Step 3: Write `quintic_sim_gfx/gui/README.md`**
```markdown
# Quintic Sim — GUI

A tkinter front-end that wraps the `quintic_sim` CLI.

## Run
    .venv/Scripts/python -m quintic_sim_gfx.gui

## What it does
1. Enter the 6 coefficients c5..c0 (default 0.0).
2. Press Run — the GUI runs your *command template* (editable at the top,
   default `.venv/Scripts/python -m quintic_sim {poly} --sage`) in a
   subprocess and renders the markdown report below.
3. Tables (Roots, Step trace) are real tables with a **horizontal
   scrollbar** for wide rows; double-click a cell to see its full text.

## Notes
- The GUI process never imports sympy/numpy; all math runs in the
  subprocess (the same code path as the CLI).
- The command template is persisted under
  `%APPDATA%\quintic_sim_gfx\config.json`.
- If the subprocess fails to start (e.g. wrong interpreter), the error is
  shown in the output pad.
```

**Step 4: Add a GUI section to `quintic_sim_gfx/README.md`** (point to `gui/README.md`, show the run command).

**Step 5: Full test suite**
```bash
env -u PYTHONPATH .venv/Scripts/python -m pytest tests/ -q
```
Expected: all green (the 148 original `quintic_sim` tests are unaffected — they import `quintic_sim`, not `quintic_sim_gfx`; the new `tests/test_gfx_*.py` all pass).

**Step 6: Manual smoke**
```bash
env -u PYTHONPATH .venv/Scripts/python -m quintic_sim_gfx.gui
```
- Type `1, -2, -3, 0, 0, -1` into the boxes → preview shows `x^5 - 2*x^4 - 3*x^3 - 1`.
- Press Run → report renders; the Roots table has 5 rows; the wide `exact` column scrolls horizontally; double-click an `exact` cell → full text popup.

**Step 7: Commit**
```bash
git add requirements-gui.txt quintic_sim_gfx/gui/README.md quintic_sim_gfx/README.md quintic_sim_gfx/gui/app.py quintic_sim_gfx/gui/__main__.py
git commit -m "gfx: packaging, DPI awareness, docs"
```

---

## 6. Files likely to change (summary)

| File | Action |
|---|---|
| `quintic_sim_gfx/__init__.py` | Modify (lazy PEP 562) |
| `quintic_sim_gfx/gui/__init__.py` | Create |
| `quintic_sim_gfx/gui/__main__.py` | Create |
| `quintic_sim_gfx/gui/config.py` | Create |
| `quintic_sim_gfx/gui/runner.py` | Create (formatter + env scrub + subprocess) |
| `quintic_sim_gfx/gui/mdrender.py` | Create (markdown → blocks) |
| `quintic_sim_gfx/gui/report_view.py` | Create (DocView + Treeview tables) |
| `quintic_sim_gfx/gui/coeff_panel.py` | Create (6 boxes + preview) |
| `quintic_sim_gfx/gui/app.py` | Create (main window) |
| `requirements-gui.txt` | Create |
| `quintic_sim_gfx/gui/README.md`, `quintic_sim_gfx/README.md` | Create / Modify |
| `tests/test_gfx_*.py` | Create (import, config, runner, mdrender, report_view, coeff_panel, app, end2end) |

Untouched: all existing pipeline modules (`cli.py`, `pipeline.py`, `report.py`, …), the original `quintic_sim/` package, and the existing `tests/test_*.py` (148 tests).

---

## 7. Tests / validation

- **Unit (headless, no display):** `test_gfx_import`, `test_gfx_config`, `test_gfx_runner` (formatter + env scrub + command build), `test_gfx_mdrender` (block model vs real report). These never import tkinter.
- **Widget (needs a display — present on this Windows host; auto-skip on `TclError`):** `test_gfx_report_view`, `test_gfx_coeff_panel`, `test_gfx_app`.
- **End-to-end:** `test_gfx_end2end` (real subprocess, no-sage fast path; sage case skips without Docker).
- **Regression:** `env -u PYTHONPATH .venv/Scripts/python -m pytest tests/ -q` → all 148 original + new tests green.
- **Manual:** launch the GUI, run the D5 vector, confirm the 5-row roots table with a working horizontal scrollbar and the double-click expand.

Every test/command runs with `env -u PYTHONPATH .venv/Scripts/python …` to avoid the V5 numpy-ABI crash.

---

## 8. Risks, tradeoffs, and open questions

| # | Item | Mitigation / decision |
|---|---|---|
| R1 | **`PYTHONPATH` pollution (V5)** can crash the wrapped subprocess at `import numpy`. | `runner.clean_env()` scrubs hermes-agent entries (Task 6, tested). Documented in the GUI README. |
| R2 | **Sage cross-check latency** (6+ s, can be longer). | Subprocess runs in a worker thread (UI stays responsive); configurable timeout; Stop button kills the `Popen`; `--sage` is a checkbox the user can disable. |
| R3 | **Very wide `exact` cells** (radical expressions, 100s of chars). | Treeview column capped at `MAX_COL=640px` → overflow drives the table's own horizontal scrollbar; double-click → wrapped full-text popup with Copy. |
| R4 | **`quintic_sim_gfx` is a copy**, not the canonical package. | The GUI wraps a *user-configurable* command; default is the user's verified `python -m quintic_sim`. The user can point the template at `quintic_sim_gfx` or any other interpreter. No coupling to which copy is "real." |
| R5 | **Lazy `__init__`** changes import semantics slightly. | Public API (`from quintic_sim_gfx import simulate/Report/…`) preserved via `__getattr__`; regression-tested (Task 2 Step 5). Existing `quintic_sim` tests unaffected (different package). |
| R6 | **tkinter look** is dated. | Acceptable for a tool GUI. `customtkinter 6.0.0` is now available in `.venv` (V4) as an optional theming layer for buttons/entries/labels/frames — **but it has no `CTkTreeview`**, so the tables stay plain `ttk.Treeview` (which is exactly what requirement 2 needs). A `ctk.set_appearance_mode`/`set_default_color_theme` call in `app.py` is a Task-13 polish item, not core. Alternative if full HTML fidelity is ever wanted: PySide6 `QWebEngineView` (§3). |
| R7 | **Headless test environments** (no display) can't run widget tests. | Widget tests use `pytest.importorskip("tkinter")` and skip on `TclError`; unit + mdrender + runner tests are fully headless. |
| R8 | **Open question — wrapped vs in-process.** The plan wraps a *command* (per the user's request) rather than calling `simulate()` in-process. This keeps the GUI light and exactly mirrors the verified CLI, but means the GUI depends on the CLI staying stable. Alternative (in-process `simulate()` with a progress callback) would give live per-stage progress but pulls sympy/numpy into the GUI process and re-introduces the V5 ABI concern. **Decision: command wrapper** (matches the request; the step-trace table already gives per-stage timing). |
| R9 | **Open question — table rendering style.** Primary = `ttk.Treeview` (fixed grid, per-table lateral scroll). Alternative = wrapped label-grid on a 2D-scrolling canvas (cells wrap, single h-scrollbar). Chosen Treeview for clean table semantics; label-grid is a drop-in enhancement if the user prefers wrapped cells. |

**Verification checklist (definition of done)**
- [ ] `env -u PYTHONPATH .venv/Scripts/python -m pytest tests/ -q` → all green (148 + new).
- [ ] `env -u PYTHONPATH .venv/Scripts/python -m quintic_sim_gfx.gui` launches.
- [ ] Six boxes default to `0.0`; entering `1,-2,-3,0,0,-1` previews `x^5 - 2*x^4 - 3*x^3 - 1`.
- [ ] Run renders the report; Roots table has 5 rows; the wide `exact` column has a working horizontal scrollbar; double-click shows full text.
- [ ] The command template is editable and persists across restarts.
- [ ] Stop kills a running subprocess; a bad interpreter shows the error in the output pad (no crash).
- [ ] `import quintic_sim_gfx` does not import `numpy`.
