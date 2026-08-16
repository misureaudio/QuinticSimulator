"""Requirement 1: the coefficient input panel.

Six input boxes, one per power of x in descending order::

    [c5] x^5 + [c4] x^4 + [c3] x^3 + [c2] x^2 + [c1] x + [c0]

Each box defaults to ``0.0`` and accepts any rational (int, decimal,
fraction, scientific notation). A live preview shows the assembled
expression (or a validation error) as the user types. Run/Stop/Clear
control the wrapped command (wired up by the app).
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .runner import format_polynomial, parse_coeff

POWERS = ("x^5", "x^4", "x^3", "x^2", "x", "1")
LABELS = ("c5", "c4", "c3", "c2", "c1", "c0")
DEFAULT = "0.0"


class CoeffPanel(ttk.LabelFrame):
    def __init__(self, master, *, on_run, on_stop, on_clear):
        super().__init__(
            master,
            text="Polynomial    [c5] x^5 + [c4] x^4 + [c3] x^3 + [c2] x^2 + [c1] x + [c0]",
        )
        self._on_run = on_run
        self.entries: list[ttk.Entry] = []

        grid = ttk.Frame(self)
        grid.pack(fill="x", padx=6, pady=4)
        for i in range(6):
            ttk.Label(grid, text=LABELS[i], width=3, anchor="e").grid(
                row=0, column=2 * i, padx=2)
            e = ttk.Entry(grid, width=8, justify="center")
            e.insert(0, DEFAULT)
            e.grid(row=0, column=2 * i + 1, padx=2)
            e.bind("<KeyRelease>", lambda _e: self._update_preview())
            e.bind("<Return>", lambda _e: self.run())
            self.entries.append(e)
            ttk.Label(grid, text=POWERS[i], anchor="w").grid(
                row=0, column=2 * i + 2, padx=2)

        self._prev = ttk.Label(self, text="", anchor="w",
                               font=("Consolas", 10))
        self._prev.pack(fill="x", padx=8, pady=(0, 4))

        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=6, pady=(0, 6))
        self.run_btn = ttk.Button(btns, text="Run \u25b6", command=self.run)
        self.run_btn.pack(side="left", padx=4)
        self.stop_btn = ttk.Button(btns, text="Stop", command=on_stop,
                                   state="disabled")
        self.stop_btn.pack(side="left", padx=4)
        ttk.Button(btns, text="Clear", command=self._clear).pack(side="left", padx=4)
        self._update_preview()

    # ------------------------------------------------------------------ API
    def get_coeffs_text(self) -> list[str]:
        return [e.get() for e in self.entries]

    def set_coeffs(self, values) -> None:
        for e, v in zip(self.entries, values):
            e.delete(0, tk.END)
            e.insert(0, str(v))
        self._update_preview()

    def preview_text(self) -> str:
        return str(self._prev.cget("text"))

    def set_running(self, running: bool) -> None:
        self.run_btn.configure(state="disabled" if running else "normal")
        self.stop_btn.configure(state="normal" if running else "disabled")

    def run(self) -> None:
        """Parse the boxes; on success hand the rationals to the app."""
        try:
            coeffs = [parse_coeff(e.get()) for e in self.entries]
        except ValueError:
            self._prev.configure(
                text="\u26a0 invalid coefficient — use numbers "
                     "(e.g. 2, -3, 0.5, 1/2)")
            return
        self._on_run(coeffs)

    # ------------------------------------------------------------ internals
    def _clear(self) -> None:
        for e in self.entries:
            e.delete(0, tk.END)
            e.insert(0, DEFAULT)
        self._update_preview()

    def _update_preview(self) -> None:
        try:
            coeffs = [parse_coeff(e.get()) for e in self.entries]
        except ValueError:
            self._prev.configure(text="\u26a0 invalid coefficient")
            return
        expr, err = format_polynomial(coeffs)
        self._prev.configure(text=err if err else f"f(x) = {expr}")
