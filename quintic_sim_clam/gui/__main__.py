"""Entry point:  python -m quintic_sim_gfx.gui"""
from __future__ import annotations

import sys


def _dpi_aware() -> None:
    """Enable per-monitor DPI awareness on Windows so the UI is crisp."""
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:  # noqa: BLE001 - best effort only
            pass


def main() -> None:
    _dpi_aware()
    import tkinter as tk

    from .app import QuinticApp

    root = tk.Tk()
    QuinticApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
