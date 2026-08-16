"""quintic_sim_gfx.gui — desktop GUI (tkinter) wrapping the quintic_sim CLI.

The GUI process never imports sympy/numpy: all computation runs in a
subprocess executing the user-configurable command template.
"""

__all__ = ["app", "coeff_panel", "config", "mdrender", "report_view", "runner"]
