"""Output pad: a vertically-scrolling document that renders report blocks.

Requirement 2 lives here: each markdown *table* becomes a ``ttk.Treeview``
with its **own horizontal scrollbar**, so wide rows (e.g. the radical
``exact`` column) scroll laterally instead of being clipped. Headings,
paragraphs, quotes, lists and code blocks are styled ``tk.Text``/labels in
a vertically scrolling canvas document. Double-clicking a table cell opens
a popup with the full wrapped cell text (and a Copy button).

No markdown parsing here — blocks come pre-parsed from ``mdrender``.
"""
from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from .mdrender import (
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

BG = "#ffffff"
CODE_BG = "#eef1f5"
QUOTE_BG = "#f3f7f3"
ROW_ODD = "#f6f8fb"
CODE_FONT = "Consolas"
UI_FONT = "Segoe UI"


class DocView(ttk.Frame):
    """The scrollable report document. One instance per app."""

    MIN_COL = 56     # px
    MAX_COL = 640    # px cap — wider content overflows into the h-scrollbar

    def __init__(self, master):
        super().__init__(master)
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=BG)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = ttk.Frame(self.canvas)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        # keep the document as wide as the viewport; blocks wrap to it
        self.canvas.bind(
            "<Configure>",
            lambda e: (
                self.canvas.itemconfigure(self._win, width=e.width),
                self._reflow(),
            ),
        )
        self.canvas.bind("<MouseWheel>", self._wheel)
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-3, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(3, "units"))

        self._text_widgets: list = []
        self._treeviews: list = []
        self._xscrollbars: list = []
        self._font_cache: dict = {}
        self._sized: list = []  # (tk.Text, font_size) pairs for reflow
        self.last_blocks: list = []

    # ------------------------------------------------------------------ utils
    def _font(self, family: str, size: int, bold: bool = False) -> tkfont.Font:
        key = (family, size, bold)
        f = self._font_cache.get(key)
        if f is None:
            f = tkfont.Font(family=family, size=size, weight="bold" if bold else "normal")
            self._font_cache[key] = f
        return f

    def _wheel(self, event):
        step = int(-event.delta / 120)
        if step:
            self.canvas.yview_scroll(step, "units")

    def _reflow(self) -> None:
        """Re-fit text blocks to the current viewport width."""
        w = self.canvas.winfo_width()
        if w < 40:
            return
        for txt, size in self._sized:
            chars = max(20, int(w / (size * 0.62)))
            if int(txt.cget("width")) != chars:
                txt.configure(width=chars)

    # ------------------------------------------------------------- public API
    def render(self, md_text: str) -> None:
        """Replace the document with the rendering of *md_text*."""
        self.clear()
        self.last_blocks = render_blocks(md_text)
        for b in self.last_blocks:
            self.add_block(b)
        self.canvas.yview_moveto(0)

    def clear(self) -> None:
        for w in self.inner.winfo_children():
            w.destroy()
        self._text_widgets.clear()
        self._treeviews.clear()
        self._xscrollbars.clear()
        self._sized.clear()
        self.last_blocks = []

    def add_block(self, b) -> None:
        if isinstance(b, Heading):
            self._add_heading(b)
        elif isinstance(b, Paragraph):
            self._add_paragraph(b)
        elif isinstance(b, Table):
            self._add_table(b)
        elif isinstance(b, Quote):
            self._add_quote(b)
        elif isinstance(b, ListBlock):
            self._add_list(b)
        elif isinstance(b, CodeBlock):
            self._add_code(b)
        elif isinstance(b, HRule):
            ttk.Separator(self.inner, orient="horizontal").pack(fill="x", padx=8, pady=6)

    # ------------------------------------------------------------- text blocks
    def _styled_text(self, inlines, *, size: int, bg: str, bold: bool = False):
        """Read-only tk.Text with tags applied to the inline runs."""
        txt = tk.Text(
            self.inner,
            wrap="word",
            bg=bg,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=4,
            pady=2,
            font=(UI_FONT, size, "bold" if bold else "normal"),
        )
        txt.tag_configure("code", font=(CODE_FONT, size), background=CODE_BG)
        txt.tag_configure("strong", font=(UI_FONT, size, "bold"))
        txt.tag_configure("em", font=(UI_FONT, size, "italic"))
        for style, text in inlines:
            txt.insert("end", text, style if style != "plain" else ())
        txt.configure(state="disabled")
        self._text_widgets.append(txt)
        self._sized.append((txt, size))
        return txt

    def _add_heading(self, b: Heading) -> None:
        size = {1: 18, 2: 15, 3: 13}.get(b.level, 12)
        w = self._styled_text(b.inlines, size=size, bg=self._window_bg(),
                              bold=True)
        w.pack(fill="x", padx=8, pady=(10, 2))

    def _window_bg(self) -> str:
        try:
            return self.winfo_toplevel().cget("background")
        except tk.TclError:
            return BG

    def _add_paragraph(self, b: Paragraph) -> None:
        w = self._styled_text(b.inlines, size=10, bg=BG)
        w.pack(fill="x", padx=8, pady=2)

    def _add_quote(self, b: Quote) -> None:
        outer = tk.Frame(self.inner, bg="#7a9c7a", bd=0, highlightthickness=0)
        inner = tk.Frame(outer, bg=QUOTE_BG, bd=0, highlightthickness=0)
        inner.pack(fill="both", expand=True, padx=(6, 8), pady=4)
        for blk in b.blocks:
            if isinstance(blk, Paragraph):
                self._styled_text(blk.inlines, size=10, bg=QUOTE_BG).pack(
                    fill="x", padx=2)
        outer.pack(fill="x", padx=8, pady=3)

    def _add_list(self, b: ListBlock) -> None:
        for idx, item_blocks in enumerate(b.items):
            prefix = f"{idx + 1}." if b.ordered else "\u2022"
            parts = []
            for blk in item_blocks:
                if isinstance(blk, Paragraph):
                    parts.append(runs_text(blk.inlines).replace("\n", " "))
            lab = ttk.Label(self.inner, text=f"{prefix}  " + " ".join(parts),
                            anchor="w", justify="left", wraplength=700)
            lab.pack(fill="x", padx=(28, 8), pady=1)

    def _add_code(self, b: CodeBlock) -> None:
        txt = tk.Text(
            self.inner,
            wrap="none",
            font=(CODE_FONT, 9),
            background="#f6f8fa",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=6,
            pady=4,
        )
        txt.insert("1.0", b.text)
        txt.configure(state="disabled")
        txt.pack(fill="x", padx=8, pady=3)
        self._text_widgets.append(txt)

    # ----------------------------------------------------------------- tables
    def _col_width(self, texts: list) -> int:
        f = self._font(CODE_FONT, 10)
        widest = 0
        for t in texts[:40]:  # cap the work on huge columns
            widest = max(widest, f.measure(t))
        return max(self.MIN_COL, min(self.MAX_COL, widest + 16))

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
        head = b.headers[0] if b.headers else []
        for ci in range(ncol):
            htxt = runs_text(head[ci]) if ci < len(head) else f"col{ci + 1}"
            tree.heading(cols[ci], text=htxt)
            col_texts = [htxt]
            for row in b.rows[:40]:
                if ci < len(row):
                    col_texts.append(runs_text(row[ci]))
            tree.column(cols[ci], width=self._col_width(col_texts),
                        minwidth=self.MIN_COL, anchor="w", stretch=False)
        for ri, row in enumerate(b.rows):
            vals = [runs_text(row[ci]) if ci < len(row) else "" for ci in range(ncol)]
            tree.insert("", "end", values=vals,
                        tags=("odd" if ri % 2 else "even",))
        tree.tag_configure("odd", background=ROW_ODD)
        tree.tag_configure("even", background=BG)

        # LATERAL scrollbar for wide rows (requirement 2)
        xsb = ttk.Scrollbar(wrap, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=xsb.set)
        tree.pack(side="left", fill="both", expand=True)
        xsb.pack(side="bottom", fill="x")
        tree.bind("<Double-Button-1>", lambda e, t=tree: self._expand_cell(t, e))

        wrap.pack(fill="x", padx=8, pady=6)
        self._treeviews.append(tree)
        self._xscrollbars.append(xsb)

    def _expand_cell(self, tree: "ttk.Treeview", event) -> None:
        """Double-click: popup with the full text of the clicked cell."""
        col = tree.identify_column(event.x)
        row = tree.identify_row(event.y)
        if not col or not row:
            return
        ci = int(col[1:]) - 1
        vals = tree.item(row, "values")
        if ci >= len(vals):
            return
        text = str(vals[ci])
        top = tk.Toplevel(self.master)
        top.title("Cell content")
        top.transient(self.master.winfo_toplevel())
        txt = tk.Text(top, wrap="word", width=80, height=18,
                      font=(CODE_FONT, 10))
        txt.insert("1.0", text)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=8, pady=8)

        def copy():
            self.master.clipboard_clear()
            self.master.clipboard_append(text)

        bar = ttk.Frame(top)
        bar.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(bar, text="Copy", command=copy).pack(side="left", padx=4)
        ttk.Button(bar, text="Close", command=top.destroy).pack(side="right", padx=4)
