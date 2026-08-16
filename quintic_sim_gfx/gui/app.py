"""Main window: command template + coefficient panel + output pad + status bar.

Wiring:  CoeffPanel --(rationals)--> runner.run_command (worker thread,
subprocess) --(markdown)--> DocView. The command template is user-editable
and persisted; the Stop button kills the live Popen via a proc_ref dict.
All cross-thread communication goes through ``root.after`` marshalling —
no tkinter widget is touched from the worker thread.
"""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import List, Optional

from . import config
from .coeff_panel import CoeffPanel
from .mdrender import render_blocks
from .report_view import DocView
from .runner import RunResult, format_polynomial, run_command

# Project root = two levels up from this file (quintic_sim_gfx/gui/app.py)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class QuinticApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.cfg = config.load()
        root.title("Quintic Solver Simulator — GUI")
        root.geometry("1000x720")
        root.minsize(780, 520)

        # ---------- top: user-configurable command template ----------
        top = ttk.Frame(root)
        top.pack(fill="x", padx=8, pady=(8, 2))
        ttk.Label(top, text="Command:").pack(side="left")
        self.cmd_var = tk.StringVar(value=self.cfg["command"])
        ttk.Entry(top, textvariable=self.cmd_var).pack(
            side="left", fill="x", expand=True, padx=6)
        self.sage_var = tk.BooleanVar(value=bool(self.cfg["sage"]))
        ttk.Checkbutton(top, text="--sage", variable=self.sage_var).pack(
            side="left", padx=4)
        ttk.Label(top, foreground="#666",
                  text="{poly} = assembled polynomial — persisted to config"
                  ).pack(side="left", padx=4)

        # ---------- middle: panel | output pad ----------
        mid = ttk.Panedwindow(root, orient="horizontal")
        mid.pack(fill="both", expand=True, padx=8, pady=4)
        self.panel = CoeffPanel(
            mid, on_run=self.on_run, on_stop=self.on_stop, on_clear=self.on_clear)
        mid.add(self.panel, weight=2)
        self.doc = DocView(mid)
        mid.add(self.doc, weight=3)
        self.doc.render(
            "# Ready\n\nEnter the coefficients (default `0.0`) and press "
            "**Run ▶**.\n\nThe report renders below; tables scroll "
            "horizontally for wide rows — double-click a cell to see its "
            "full text.\n"
        )

        # ---------- bottom: status bar ----------
        self.status = ttk.Label(root, text="Idle", anchor="w", relief="sunken")
        self.status.pack(fill="x", side="bottom")

        self._proc_ref: dict = {}
        self._worker: Optional[threading.Thread] = None
        # Thread-safe handoff: the worker (not the main thread) must never
        # touch tkinter — root.after() from another thread raises
        # "main thread is not in main loop" on Python 3.13/Windows.
        # Instead the worker puts results on this queue and the main loop
        # drains it on a 100 ms poll.
        self._outbox: "queue.Queue[RunResult]" = queue.Queue()
        self._polling = False
        self.cmd_var.trace_add("write", lambda *a: self._save_cfg())
        self.sage_var.trace_add("write", lambda *a: self._save_cfg())

    # ------------------------------------------------------------------ API
    def on_run(self, coeffs: List) -> None:
        expr, err = format_polynomial(coeffs)
        if err:
            self._status(f"\u26a0 {err}")
            return
        self._save_cfg()
        # Capture tk variable values HERE (main thread). tkinter is not
        # thread-safe: the worker must never touch widgets or StringVars.
        cmd = self.cmd_var.get()
        sage = bool(self.sage_var.get())
        timeout = int(self.cfg.get("timeout", 300))
        self.panel.set_running(True)
        self._proc_ref = {}
        self._status(f"Running: {cmd} …")
        self._worker = threading.Thread(
            target=self._worker_fn, args=(expr, cmd, sage, timeout), daemon=True)
        self._worker.start()
        self._ensure_polling()

    def on_stop(self) -> None:
        p = self._proc_ref.get("p")
        if p is not None and p.poll() is None:
            p.kill()
            self._status("Stop requested — killing subprocess")
        else:
            self._status("Nothing running")

    def on_clear(self) -> None:
        self.doc.render("# Cleared\n")
        self._status("Cleared")

    # ------------------------------------------------------------ internals
    def _worker_fn(self, expr: str, cmd: str, sage: bool, timeout: int) -> None:
        res = run_command(
            cmd,
            expr,
            sage=sage,
            cwd=str(PROJECT_ROOT),
            timeout=timeout,
            proc_ref=self._proc_ref,
        )
        self._outbox.put(res)  # main loop picks it up in _poll_outbox

    def _ensure_polling(self) -> None:
        if not self._polling:
            self._polling = True
            self.root.after(100, self._poll_outbox)

    def _poll_outbox(self) -> None:
        try:
            while True:
                self._on_done(self._outbox.get_nowait())
        except queue.Empty:
            pass
        busy = self._worker is not None and self._worker.is_alive()
        if busy or not self._outbox.empty():
            self.root.after(100, self._poll_outbox)
        else:
            self._polling = False

    def _on_done(self, res: RunResult) -> None:
        self.panel.set_running(False)
        if res.ok:
            self.doc.render(res.stdout)
            self._last_blocks = render_blocks(res.stdout)
            self._status(
                f"OK  ({res.duration:.2f}s)  •  "
                f"{len(res.stdout.splitlines())} lines of report")
        else:
            detail = (res.stderr or res.stdout).strip()
            if res.timed_out:
                detail = f"timed out after {self.cfg.get('timeout')}s\n\n{detail}"
            self.doc.render(
                f"# Error (exit {res.returncode})\n\n"
                f"```\n{detail[:20000]}\n```\n")
            self._status(f"FAILED  exit={res.returncode}"
                         + ("  (timed out)" if res.timed_out else ""))

    def _status(self, msg: str) -> None:
        self.status.configure(text=msg)

    def _save_cfg(self) -> None:
        self.cfg["command"] = self.cmd_var.get()
        self.cfg["sage"] = bool(self.sage_var.get())
        try:
            config.save(self.cfg)
        except OSError:
            pass  # config is best-effort; never block the UI on it
