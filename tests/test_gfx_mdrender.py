"""mdrender.py — markdown-it-py token stream -> block model."""
from quintic_sim_gfx.gui import mdrender
from quintic_sim_gfx.gui.mdrender import (
    CodeBlock,
    HRule,
    Heading,
    ListBlock,
    Paragraph,
    Quote,
    Table,
    render_blocks,
    runs_text,
)

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

1. first
2. second

`inline code` and **bold** and *em*

---

```
fenced code
```
"""


def test_block_counts():
    b = render_blocks(SAMPLE)
    kinds = [type(x).__name__ for x in b]
    assert kinds.count("Heading") == 2
    assert kinds.count("Table") == 1
    assert "Quote" in kinds
    assert kinds.count("ListBlock") == 2
    assert "CodeBlock" in kinds
    assert "HRule" in kinds


def test_heading_levels():
    b = render_blocks(SAMPLE)
    heads = [x for x in b if isinstance(x, Heading)]
    assert [h.level for h in heads] == [1, 2]
    assert runs_text(heads[0].inlines) == "Quintic Solver Report"


def test_table_shape():
    t = next(x for x in render_blocks(SAMPLE) if isinstance(x, Table))
    assert len(t.headers) == 1
    assert [runs_text(c) for c in t.headers[0]] == ["#", "exact", "numeric (15 digits)", "verified"]
    assert len(t.rows) == 2
    assert len(t.rows[0]) == 4


def test_wide_cell_preserved_verbatim():
    t = next(x for x in render_blocks(SAMPLE) if isinstance(x, Table))
    assert runs_text(t.rows[0][1]) == "CRootOf(x**5 - 2, 0)"
    assert runs_text(t.rows[1][2]) == "-0.755 + 0.951*I"


def test_inline_runs_styles():
    b = render_blocks(SAMPLE)
    # the last paragraph before the hrule mixes code/strong/em
    para = [x for x in b if isinstance(x, Paragraph)][-1]
    styles = {s for s, _ in para.inlines}
    assert {"code", "strong", "em"} <= styles
    assert runs_text(para.inlines) == "inline code and bold and em"


def test_quote_and_lists():
    b = render_blocks(SAMPLE)
    q = next(x for x in b if isinstance(x, Quote))
    assert any(isinstance(blk, Paragraph) for blk in q.blocks)
    ul = next(x for x in b if isinstance(x, ListBlock) and not x.ordered)
    assert len(ul.items) == 2
    ol = next(x for x in b if isinstance(x, ListBlock) and x.ordered)
    assert len(ol.items) == 2


def test_code_block_content():
    cb = next(x for x in render_blocks(SAMPLE) if isinstance(x, CodeBlock))
    assert cb.text == "fenced code\n"


def test_empty_input():
    assert render_blocks("") == []
    assert render_blocks("   \n  \n") == []


def test_real_report_fixture():
    """The actual report from the pipeline: 2 tables, 5 root rows, 9 trace rows."""
    from pathlib import Path

    p = Path(__file__).resolve().parents[1] / "QuinticSolverReport_v0d.md"
    if not p.exists():
        import pytest

        pytest.skip("fixture report not present")
    md = p.read_text(encoding="utf-8")
    b = render_blocks(md)
    tables = [x for x in b if isinstance(x, Table)]
    assert len(tables) == 2
    roots, trace = tables
    assert len(roots.rows) == 5
    assert all(len(r) == 4 for r in roots.rows)
    assert len(trace.rows) == 9
    assert all(len(r) == 4 for r in trace.rows)
