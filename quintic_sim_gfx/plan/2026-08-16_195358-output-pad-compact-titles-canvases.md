# Output-Pad Vertical Space — Compact Titles/Canvases

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Eliminate the large empty "page" gaps between titles and data canvases in the right-hand output pad, so the report is compact and the tables are visible without scrolling through dead space.

**Architecture:** The `DocView` output pad (`quintic_sim_gfx/gui/report_view.py`) renders each markdown block as a packed widget inside a vertical-scroll `Canvas`. The bug is that every `tk.Text` (headings, paragraphs, quote text, code blocks) is created **without a `height`**, so Tk defaults each to **24 display-lines tall** (~844–988px) even when it holds one line. `pack(fill="x")` stretches the width but never the height, so each title/paragraph reserves a full page of vertical space. The fix sizes each `tk.Text` to its **actual display-line count** (a `+1displayline` index walk) and re-sizes on canvas resize. No markdown parsing, table, or scroll logic changes.

**Tech Stack:** Python 3.13, tkinter (`tk.Text`, `ttk`), existing `DocView`.

**Measured evidence (fixture `QuinticSolverReport_v0d.md`, 1000×720 window):**

| Block | Text | actual height (buggy) |
|---|---|---|
| H1 | `Quintic Solver Report` (1 line) | **988 px** |
| H2 | `Galois group (S3)` (1 line) | **844 px** |
| H2 | `Factorization (S2)` (1 line) | **844 px** |
| para | `Input: …` (3 lines) | 556 px |
| **Whole document** | | **10760 px** (yview range = 0.06, i.e. only 6% visible) |

After the fix (verified in-memory): document = **1733 px** (6.2× smaller), H1 = 45px, H2 = 39px, yview range = 0.38. The two `Treeview` tables keep their own horizontal scrollbars unchanged.

---

## Root cause (precise)

`_styled_text()` (`report_view.py:136-157`) and `_add_code()` (`report_view.py:196-211`) build `tk.Text(...)` **with no `height=`**. Tk's `Text` default height is **24**. Because the widgets are packed with `fill="x"` (not `fill="both"`), packer gives them their *requested* height (24 lines) while stretching width to the container. Result: a 1-line heading still reserves 24 lines of canvas.

`_reflow()` (`report_view.py:91-99`) currently only sets a width heuristic (`chars = w/(size*0.62)`); it never touches height, so it cannot fix the gap.

**Why the `+1displayline` walk (not `count(...,'displaylines')`):** on this Tk 8.6 build, `Text.count` with the `displaylines` option returns `None` or garbage for disabled/realized widgets (measured: `None` for headings, off-by-one for others). The portable, correct idiom is an index walk (copy-paste-ready in Task 2):

```python
def _display_lines(self, t, end="end-1c") -> int:
    n, idx = 1, "1.0"
    while True:
        nxt = t.index(f"{idx}+1displayline")
        if t.compare(nxt, ">=", end):
            break
        n += 1
        idx = nxt
    return n
```

---

## Files likely to change

- Modify: `quintic_sim_gfx/gui/report_view.py` — add `_display_lines`, add `_size_to_content`, call it from `_styled_text`/`_add_code`, rewrite `_reflow`.
- Test: `tests/test_gfx_report_view.py` — add compactness assertions.

No other file changes. `mdrender.py`, `coeff_panel.py`, `app.py`, `runner.py`, `config.py` are untouched.

---

### Task 1: Add a failing compactness test

**Objective:** Capture the desired behavior (1-line heading is short, document is compact) so the fix is verifiable.

**Files:**
- Test: `tests/test_gfx_report_view.py`

**Step 1: Add the test**

Append to `tests/test_gfx_report_view.py`:

```python
def test_heading_is_compact_not_24_lines():
    """A 1-line heading must occupy ~1 line, not the 24-line Text default."""
    r = _root()
    v = DocView(r)
    v.render("# Short Title\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    r.update_idletasks()
    r.update()
    headings = [w for w in v.inner.winfo_children() if w.winfo_class() == "Text"]
    assert headings, "expected a Text heading widget"
    h1 = headings[0]
    # default-buggy height for a size-18 heading is ~900px; compact is <120px
    assert h1.winfo_height() < 120, f"heading too tall: {h1.winfo_height()}px"
    # the whole document must be far smaller than the 10760px buggy case
    assert v.inner.winfo_height() < 2500, f"document too tall: {v.inner.winfo_height()}px"
    r.destroy()
```

**Step 2: Run to verify failure**

Run: `env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_report_view.py::test_heading_is_compact_not_24_lines -v`
Expected: **FAIL** — `heading too tall: ~988px` (the 24-line default).

**Step 3: Commit the failing test**

```bash
git add tests/test_gfx_report_view.py
git commit -m "test(gfx): heading must be compact, not the 24-line Text default"
```

---

### Task 2: Add `_display_lines` and `_size_to_content` helpers

**Objective:** Provide the correct display-line measurement and a single routine that sizes a `tk.Text` to its content.

**Files:**
- Modify: `quintic_sim_gfx/gui/report_view.py` (add two methods near `_reflow`, ~line 91)

**Step 1: Add the methods**

Insert after `_reflow` (keep `_reflow` for now; Task 3 rewrites it):

```python
    def _display_lines(self, t, end: str = "end-1c") -> int:
        """Number of wrapped display lines in a tk.Text (portable idiom).

        `Text.count(..., 'displaylines')` is unreliable on this Tk build
        (returns None/off-by-one for disabled widgets), so walk indices.
        """
        n, idx = 1, "1.0"
        while True:
            nxt = t.index(f"{idx}+1displayline")
            if t.compare(nxt, ">=", end):
                break
            n += 1
            idx = nxt
        return n

    def _size_to_content(self, t) -> None:
        """Shrink a read-only tk.Text to its actual display height.

        Must be called after the widget's width is settled (i.e. after a
        geometry pass) so the wrap is final. Re-enables state only to set
        `height`, then restores `disabled`.
        """
        was_disabled = str(t.cget("state")) == "disabled"
        if was_disabled:
            t.configure(state="normal")
        t.configure(height=max(1, self._display_lines(t)))
        if was_disabled:
            t.configure(state="disabled")
```

**Step 2: Verify it imports cleanly**

Run: `env -u PYTHONPATH .venv/Scripts/python -c "import quintic_sim_gfx.gui.report_view"`
Expected: no output (clean import).

**Step 3: Run the failing test (still fails — helpers not wired yet)**

Run: `env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_report_view.py::test_heading_is_compact_not_24_lines -v`
Expected: still **FAIL** (helpers exist but aren't called).

**Step 4: Commit**

```bash
git add quintic_sim_gfx/gui/report_view.py
git commit -m "feat(gfx): _display_lines + _size_to_content for compact Text"
```

---

### Task 3: Wire sizing into `_styled_text` and `_add_code`; rewrite `_reflow`

**Objective:** Apply content-height to every text block and re-apply on resize.

**Files:**
- Modify: `quintic_sim_gfx/gui/report_view.py:136-157` (`_styled_text`), `:196-211` (`_add_code`), `:91-99` (`_reflow`)

**Step 1: Size in `_styled_text`** — after `txt.configure(state="disabled")` (line 154), add:

```python
        txt.configure(state="disabled")
        self._text_widgets.append(txt)
        self._sized.append((txt, size))
        self._size_to_content(txt)   # <-- NEW: collapse to content height
        return txt
```

**Step 2: Size in `_add_code`** — after `txt.configure(state="disabled")` (line 209), add:

```python
        txt.insert("1.0", b.text)
        txt.configure(state="disabled")
        txt.pack(fill="x", padx=8, pady=3)
        self._text_widgets.append(txt)
        self._sized.append((txt, 9))  # keep in _sized so _reflow re-sizes it
        self._size_to_content(txt)    # <-- NEW
```

**Step 3: Rewrite `_reflow` to re-size heights on width change** — replace the body (lines 96-99):

```python
    def _reflow(self) -> None:
        """Re-fit text blocks to the current viewport width.

        `pack(fill="x")` already stretches each Text to the canvas width,
        so the wrap is final here; we only need to re-collapse the height
        to the new display-line count. Setting `width` is intentionally
        avoided — forcing a requested width fights the packer and can
        create a resize feedback loop.
        """
        w = self.canvas.winfo_width()
        if w < 40:
            return
        for txt, _size in self._sized:
            self._size_to_content(txt)
```

**Step 4: Run the target test**

Run: `env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_report_view.py::test_heading_is_compact_not_24_lines -v`
Expected: **PASS**.

**Step 5: Run the whole report_view suite (no regressions)**

Run: `env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_report_view.py -v`
Expected: all PASS (existing 6 + new 1 = 7).

**Step 6: Commit**

```bash
git add quintic_sim_gfx/gui/report_view.py
git commit -m "fix(gfx): collapse Text blocks to content height; reflow on resize"
```

---

### Task 4: Verify the real report is compact end-to-end

**Objective:** Prove the user-visible symptom (huge dead space before the tables) is gone on the actual report.

**Files:** none (verification only)

**Step 1: Instrumented render (read-only probe)**

Run:
```bash
env -u PYTHONPATH .venv/Scripts/python -c "
import tkinter as tk
from pathlib import Path
from quintic_sim_gfx.gui.__main__ import _dpi_aware
from quintic_sim_gfx.gui.app import QuinticApp
_dpi_aware()
root = tk.Tk(); app = QuinticApp(root); root.geometry('1000x720')
app.doc.render(Path('QuinticSolverReport_v0d.md').read_text(encoding='utf-8'))
root.update_idletasks(); root.update()
print('inner height =', app.doc.inner.winfo_height(), 'px')
print('yview range  =', app.doc.canvas.yview())
for w in app.doc.inner.winfo_children()[:8]:
    print('  y=%4d h=%4d %-8s' % (w.winfo_y(), w.winfo_height(), w.winfo_class()))
root.destroy()
"
```
Expected: `inner height` ≈ **1700–1800 px** (was 10760), yview range ≈ **0.38** (was 0.06), H1 `h` ≈ 45, H2 `h` ≈ 39, tables present.

**Step 2: Full GUI test suite**

Run: `env -u PYTHONPATH .venv/Scripts/python -m pytest tests/test_gfx_report_view.py tests/test_gfx_app.py -v`
Expected: all PASS.

**Step 3: Full project suite (no regressions)**

Run: `env -u PYTHONPATH .venv/Scripts/python -m pytest tests/ -q`
Expected: **207 passed** (or 208 with the new test).

**Step 4: Commit (if any fixups were needed)**

```bash
git add -A quintic_sim_gfx/gui/ tests/
git commit -m "test(gfx): verify compact output pad on real report"
```

---

## Tests / validation summary

- `tests/test_gfx_report_view.py::test_heading_is_compact_not_24_lines` (new) — heading <120px, document <2500px.
- Existing `test_gfx_report_view.py` (6 tests) — tables, lateral scrollbar, clear, real-fixture render must stay green.
- `tests/test_gfx_app.py` — end-to-end (incl. Sage) must stay green.
- Full `tests/` — 207+ passed.

## Risks, tradeoffs, open questions

- **Resize feedback loop (mitigated):** the old `_reflow` set `width`, which can fight `pack(fill="x")` and trigger `<Configure>` re-entrancy. The new `_reflow` only sets `height` (never `width`), so it cannot loop. If a flicker is observed on window resize, guard with a `self._reflowing` flag set around the height updates.
- **`height` is a *minimum*:** Tk `Text` `height` is the minimum number of lines; with `wrap="word"` and `fill="x"` it renders exactly that many, so content-height is achieved. If a future block needs to *grow* beyond the set height (it won't for read-only, fully-inserted text), re-run `_size_to_content`.
- **`displaylines` count unreliable (documented):** use the index walk, not `Text.count('displaylines')` — measured to return `None`/off-by-one on this Tk 8.6 / Python 3.13 build.
- **Treeview row count (optional, out of scope):** tables cap at `height=min(12, max(3, len(rows)))`. If the user wants even more compactness, lower the 12 — but that changes table visibility, so it's a separate decision, not part of this fix.
- **Windows-only measurement:** heights above are at 100% DPI. At 150% DPI the absolute px scale up, but the *ratio* fix (6.2×) holds because it's line-based.

## Out of scope

- No change to markdown parsing (`mdrender.py`), table rendering/lateral scroll, cell-expand popup, coefficient panel, runner, or config.
- No change to the `quintic_sim/` original package (read-only reference).
- No theme/DPI changes.
