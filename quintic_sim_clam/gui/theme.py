"""Light/dark theme for the GUI: palettes + application.

``customtkinter`` is imported lazily inside :func:`apply` (no-op when
absent), so this module — and the whole GUI — works without it. The
document area (``report_view.DocView``) takes its colors from the palette
dict via ``set_palette``; the chrome is styled through ``ttk.Style`` and,
once ctk widgets exist (Phase 2), through
``customtkinter.set_appearance_mode``.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

__all__ = ["PALETTES", "THEME_NAMES", "normalize", "apply"]

THEME_NAMES = ("light", "dark")

# Role map (documented for palette consumers):
#   window         root / frames / label backgrounds
#   text           primary text
#   muted          secondary text (hint labels)
#   entry_bg       entry / combobox fields
#   button_bg / button_hover / disabled_bg / disabled_fg
#   border         separators, widget borders
#   selection / selection_fg   treeview + entry selection
#   doc_bg         report canvas background
#   code_bg        inline code spans inside text
#   code_block_bg  fenced code blocks
#   quote_bg / quote_border
#   row_even / row_odd   table (Treeview) row backgrounds
PALETTES: dict = {
    "light": {
        "window": "#f0f0f0",
        "text": "#1e1e1e",
        "muted": "#666666",
        "entry_bg": "#ffffff",
        "button_bg": "#e1e1e1",
        "button_hover": "#eaeaea",
        "disabled_bg": "#d6d3ce",
        "disabled_fg": "#6d6d6d",
        "border": "#a0a0a0",
        "selection": "#0078d7",
        "selection_fg": "#ffffff",
        "doc_bg": "#ffffff",
        "code_bg": "#eef1f5",
        "code_block_bg": "#f6f8fa",
        "quote_bg": "#f3f7f3",
        "quote_border": "#7a9c7a",
        "row_even": "#ffffff",
        "row_odd": "#f6f8fb",
    },
    "dark": {
        "window": "#1e1e1e",
        "text": "#d4d4d4",
        "muted": "#9d9d9d",
        "entry_bg": "#2d2d2d",
        "button_bg": "#3a3a3a",
        "button_hover": "#464646",
        "disabled_bg": "#2d2d2d",
        "disabled_fg": "#7a7a7a",
        "border": "#4a4a4a",
        "selection": "#094771",
        "selection_fg": "#ffffff",
        "doc_bg": "#1e1e1e",
        "code_bg": "#2d2d2d",
        "code_block_bg": "#262626",
        "quote_bg": "#2a332a",
        "quote_border": "#5a8a5a",
        "row_even": "#1e1e1e",
        "row_odd": "#252629",
    },
}


def normalize(name) -> str:
    """Coerce a persisted/CLI value to a valid theme name."""
    return name if name in THEME_NAMES else "light"


def _set_ctk_appearance(mode: str) -> None:
    """customtkinter is optional: no-op when not installed."""
    try:
        import customtkinter as ctk
    except ImportError:
        return
    try:
        ctk.set_appearance_mode(mode)
    except Exception:  # noqa: BLE001 — theming is best-effort
        pass


def apply(root: tk.Tk, name, doc=None) -> str:
    """Apply *name* ("light"/"dark") to *root* and, when given, the
    document view *doc* (duck-typed: must have ``set_palette(pal)``).

    Idempotent and safe to call repeatedly (live switching). Returns the
    normalized theme name.
    """
    theme_name = normalize(name)
    pal = PALETTES[theme_name]
    root.configure(bg=pal["window"])
    style = ttk.Style(root)
    # clam is the most styleable built-in theme: the default vista theme
    # renders the Treeview header with the native Windows (always light)
    # look and ignores Treeview.Heading background/foreground options.
    # clam honors every style.configure below, in both themes.
    style.theme_use("clam")
    style.configure("TFrame", background=pal["window"])
    style.configure("TLabel", background=pal["window"], foreground=pal["text"])
    style.configure("TLabelframe", background=pal["window"],
                    foreground=pal["text"])
    style.configure("TLabelframe.Label", background=pal["window"],
                    foreground=pal["text"])
    style.configure("TEntry", fieldbackground=pal["entry_bg"],
                    foreground=pal["text"], insertcolor=pal["text"],
                    background=pal["entry_bg"])
    style.configure("TCheckbutton", background=pal["window"],
                    foreground=pal["text"])
    style.map("TCheckbutton", background=[("active", pal["window"])])
    style.configure("TButton", background=pal["button_bg"],
                    foreground=pal["text"], bordercolor=pal["border"],
                    focuscolor=pal["selection"])
    style.map("TButton",
              background=[("active", pal["button_hover"]),
                          ("disabled", pal["disabled_bg"])],
              foreground=[("disabled", pal["disabled_fg"])])
    style.configure("TCombobox", fieldbackground=pal["entry_bg"],
                    background=pal["window"], foreground=pal["text"],
                    arrowcolor=pal["text"], bordercolor=pal["border"])
    style.map("TCombobox",
              fieldbackground=[("readonly", pal["entry_bg"])],
              foreground=[("readonly", pal["text"])])
    style.configure("Treeview", background=pal["row_even"],
                    fieldbackground=pal["row_even"],
                    foreground=pal["text"])
    style.configure("Treeview.Heading", background=pal["button_bg"],
                    foreground=pal["text"], bordercolor=pal["border"],
                    relief="raised")
    style.map("Treeview",
              background=[("selected", pal["selection"])],
              foreground=[("selected", pal["selection_fg"])])
    style.configure("TSeparator", background=pal["border"])
    style.configure("TPanedwindow", background=pal["window"])
    style.configure("TScrollbar", background=pal["entry_bg"],
                    troughcolor=pal["window"], bordercolor=pal["border"],
                    arrowcolor=pal["text"])
    if doc is not None and hasattr(doc, "set_palette"):
        doc.set_palette(pal)
    _set_ctk_appearance("dark" if theme_name == "dark" else "light")
    return theme_name
