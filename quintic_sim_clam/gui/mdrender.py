"""markdown-it-py -> lightweight block model (no tkinter import).

The report markdown is tokenized with markdown-it-py (CommonMark + GFM
tables) and turned into a small tree of block dataclasses:

    Heading, Paragraph, Table, Quote, List, CodeBlock, HRule

Each text run carries a style tag (plain/code/strong/em) so the view layer
can map runs to tk Text tags without re-parsing anything. The token stream
was verified against the real report (see plan V6); the parser below is a
straight walk over it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from markdown_it import MarkdownIt

__all__ = [
    "Run",
    "Heading",
    "Paragraph",
    "Table",
    "Quote",
    "ListBlock",
    "CodeBlock",
    "HRule",
    "render_blocks",
    "runs_text",
]

# (style, text); style in {plain, code, strong, em}
Run = Tuple[str, str]


@dataclass
class Heading:
    level: int
    inlines: List[Run]


@dataclass
class Paragraph:
    inlines: List[Run]


@dataclass
class Table:
    headers: List[List[Run]] = field(default_factory=list)  # usually 1 row
    rows: List[List[List[Run]]] = field(default_factory=list)


@dataclass
class Quote:
    blocks: list = field(default_factory=list)


@dataclass
class ListBlock:
    ordered: bool
    items: list = field(default_factory=list)  # list[list[block]]


@dataclass
class CodeBlock:
    lang: str
    text: str


@dataclass
class HRule:
    pass


def runs_text(runs: List[Run]) -> str:
    """Flatten runs to plain text (used for Treeview cell values)."""
    return "".join(text for _, text in runs)


# ---------------------------------------------------------------------------
# inline handling
# ---------------------------------------------------------------------------
def _runs(tok) -> List[Run]:
    """Flatten an inline token into (style, text) runs, merging neighbors."""
    out: List[Run] = []
    stack: List[str] = []

    def cur() -> str:
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
            if stack:
                stack.pop()
        elif t == "em_open":
            stack.append("em")
        elif t == "em_close":
            if stack:
                stack.pop()
        elif t in ("softbreak", "hardbreak"):
            out.append((cur(), "\n"))
    # merge adjacent same-style runs
    merged: List[Run] = []
    for s, text in out:
        if merged and merged[-1][0] == s:
            merged[-1] = (s, merged[-1][1] + text)
        else:
            merged.append((s, text))
    return merged


# ---------------------------------------------------------------------------
# block walk
# ---------------------------------------------------------------------------
def _table(toks, i: int):
    """Parse a table starting at toks[i] == table_open. Returns (Table, i_after)."""
    headers: List[List[Run]] = []
    rows: List[List[List[Run]]] = []
    target = None  # "head" | "body" | None
    row: List[List[Run]] | None = None
    i += 1
    while i < len(toks) and toks[i].type != "table_close":
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
            # cell content is the next token (an inline)
            row.append(_runs(toks[i + 1]))
            i += 2
        elif tt in ("th_close", "td_close"):
            i += 1
        elif tt == "tr_close":
            if row is not None:
                (headers if target == "head" else rows).append(row)
            row, i = None, i + 1
        else:  # defensive: skip anything unexpected
            i += 1
    return Table(headers, rows), i + 1  # skip table_close


def _match_end(toks, i: int, opens, closes) -> int:
    """Index of the close token matching the open at toks[i] (inclusive)."""
    depth = 0
    j = i
    while j < len(toks):
        if toks[j].type in opens:
            depth += 1
        elif toks[j].type in closes:
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return j


def _build(toks, i: int, end: int):
    blocks: list = []
    while i < end:
        t = toks[i]
        ty = t.type
        if ty == "heading_open":
            blocks.append(Heading(int(t.tag[1]), _runs(toks[i + 1])))
            i += 3
        elif ty == "paragraph_open":
            blocks.append(Paragraph(_runs(toks[i + 1])))
            i += 3
        elif ty == "table_open":
            tbl, i = _table(toks, i)
            blocks.append(tbl)
        elif ty == "blockquote_open":
            e = _match_end(toks, i, ("blockquote_open",), ("blockquote_close",))
            inner = _build(toks, i + 1, e)
            blocks.append(Quote(inner))
            i = e + 1
        elif ty in ("bullet_list_open", "ordered_list_open"):
            ordered = ty == "ordered_list_open"
            e = _match_end(
                toks, i,
                ("bullet_list_open", "ordered_list_open"),
                ("bullet_list_close", "ordered_list_close"),
            )
            items = _list_items(toks, i + 1, e)
            blocks.append(ListBlock(ordered, items))
            i = e + 1
        elif ty in ("fence", "code_block"):
            blocks.append(CodeBlock(t.info or "", t.content))
            i += 1
        elif ty == "hr":
            blocks.append(HRule())
            i += 1
        else:  # defensive: skip anything unexpected
            i += 1
    return blocks


def _list_items(toks, i: int, end: int) -> list:
    items: list = []
    while i < end:
        if toks[i].type == "list_item_open":
            e = _match_end(toks, i, ("list_item_open",), ("list_item_close",))
            inner = _build(toks, i + 1, e)
            items.append(inner)
            i = e + 1
        else:
            i += 1
    return items


def render_blocks(md_text: str) -> list:
    """Parse report markdown into a flat list of top-level blocks."""
    md = MarkdownIt("commonmark").enable("table")
    toks = md.parse(md_text)
    return _build(toks, 0, len(toks))
