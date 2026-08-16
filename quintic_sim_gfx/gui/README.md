# Quintic Sim — GUI

A tkinter front-end for the Quintic Solver Simulator. It is a thin
**wrapper around a user-configurable command** (by default the verified
`.venv/Scripts/python -m quintic_sim {poly} --sage`): the GUI never
computes anything itself — it assembles the polynomial from the
coefficient boxes, runs the command in a subprocess, and renders the
markdown report it prints.

## Run

```bash
.venv/Scripts/python -m quintic_sim_gfx.gui
```

## What it does

1. **Coefficient panel** — six input boxes, one per power of `x` in
   descending order, each defaulting to `0.0`:

   ```
   [c5] x^5 + [c4] x^4 + [c3] x^3 + [c2] x^2 + [c1] x + [c0]
   ```

   Any rational is accepted (int, decimal, `1/2`, `1e3`). A live preview
   shows the assembled expression as you type, e.g.
   `f(x) = x^5 - 2*x^4 - 3*x^3 - 1`. Enter also triggers Run.
2. **Run / Stop / Clear** — Run executes the command template in a worker
   thread (the UI stays responsive); Stop kills the subprocess; Clear
   resets the document.
3. **Output pad** — the markdown report rendered as a scrollable
   document. Each table (Roots, Step trace) is a real table widget with
   its **own horizontal scrollbar**, so wide rows (e.g. the radical
   `exact` column) scroll laterally instead of being clipped.
   **Double-click any cell** to open a popup with the full wrapped text
   and a Copy button.

## The command template (user-configurable)

The command is shown in the editable field at the top of the window.
`{poly}` is replaced with the assembled polynomial (shell-quoted). The
`--sage` checkbox adds/removes the `--sage` flag. Both are persisted to
`%APPDATA%\quintic_sim_gfx\config.json`, so you can point the GUI at any
interpreter or package copy, e.g.:

```
.venv/Scripts/python -m quintic_sim_gfx {poly} --sage
```

## Module map

| File | Responsibility |
|---|---|
| `__main__.py` | entry point (`python -m quintic_sim_gfx.gui`), DPI awareness |
| `config.py` | persistent command template + prefs (JSON) |
| `runner.py` | coeffs → expression, command building, `PYTHONPATH` scrub, killable subprocess |
| `mdrender.py` | markdown-it-py tokens → block model (no tkinter) |
| `report_view.py` | scrollable document; tables → Treeview with lateral scroll + cell expand |
| `coeff_panel.py` | the six coefficient boxes, live preview, Run/Stop/Clear |
| `app.py` | main window wiring, worker thread, thread-safe outbox, status bar |

## Notes & pitfalls

- The GUI process imports only `tkinter` + `markdown-it-py` — never
  sympy/numpy. All math happens in the subprocess (the same code path as
  the CLI).
- The agent shell exports a `PYTHONPATH` pointing at a different venv
  (cp311 numpy) that crashes `import numpy` under the project's cp313
  venv; `runner.clean_env()` strips those entries from the subprocess
  environment automatically.
- Without Docker the `--sage` cross-check is reported as `skipped` by the
  pipeline — everything else is unaffected.
- Tests: `tests/test_gfx_*.py` (headless unit tests + widget tests +
  end-to-end through the real CLI).
