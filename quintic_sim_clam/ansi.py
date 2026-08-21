"""ANSI SGR colorization of report markdown for terminal output.

No tkinter, no third-party dependencies: plain regex painting. The
painted output is the same markdown text with SGR escapes added —
``strip_ansi(paint_markdown(md, p)) == md`` always holds. Emission is
gated by :func:`color_enabled` (tty / NO_COLOR / FORCE_COLOR) so piped
output (e.g. the GUI's subprocess) never receives escapes.
"""
from __future__ import annotations

import os
import re

__all__ = ["PALETTES", "color_enabled", "paint_markdown", "strip_ansi"]

# SGR role codes; "dark" palette targets dark terminal backgrounds
# (bright accents), "light" palette targets light backgrounds.
PALETTES = {
    "light": {"heading": "1;34", "success": "32", "warn": "33",
              "bold": "1", "code": "35", "dim": "2"},
    "dark": {"heading": "1;96", "success": "92", "warn": "93",
             "bold": "1", "code": "94", "dim": "2"},
}

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_CODE_SPAN_RE = re.compile(r"(`[^`\n]*`)")
# the **markers stay in the output; only the inner text is wrapped
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_TABLE_SEP_RE = re.compile(r"^\|(?:\s*:?-{2,}:?\s*\|)+$")


def strip_ansi(text: str) -> str:
    """Remove SGR escapes (used by tests to prove the round-trip)."""
    return _ANSI_RE.sub("", text)


def color_enabled(stream) -> bool:
    """True when it is safe to emit ANSI codes on *stream*.

    FORCE_COLOR forces emission (explicit user opt-in wins over the
    NO_COLOR convention); NO_COLOR then disables; else the stream must
    be a tty.
    """
    if os.environ.get("FORCE_COLOR"):
        return True
    if os.environ.get("NO_COLOR"):
        return False
    try:
        return bool(stream.isatty())
    except (AttributeError, ValueError):
        return False


def _wrap(code: str, text: str) -> str:
    return f"\x1b[{code}m{text}\x1b[0m"


def _paint_line(line: str, pal: dict) -> str:
    if line.startswith("#"):
        return _wrap(pal["heading"], line)
    if _TABLE_SEP_RE.match(line):
        return _wrap(pal["dim"], line)
    out = line
    out = out.replace("\u2705", _wrap(pal["success"], "\u2705"))
    # warning glyph: with and without the U+FE0F variation selector,
    # in one pass (a second .replace would re-wrap the first result)
    out = re.sub(r"\u26a0(\ufe0f)?",
                 lambda m: _wrap(pal["warn"], m.group(0)), out)
    parts = _CODE_SPAN_RE.split(out)
    for i in range(1, len(parts), 2):          # code spans (odd indices)
        parts[i] = _wrap(pal["code"], parts[i])
    for i in range(0, len(parts), 2):          # bold runs in plain parts
        parts[i] = _BOLD_RE.sub(
            lambda m: "**" + _wrap(pal["bold"], m.group(1)) + "**",
            parts[i])
    return "".join(parts)


def paint_markdown(md: str, palette: dict) -> str:
    """Paint report markdown line by line (see module docstring)."""
    return "\n".join(_paint_line(line, palette) for line in md.split("\n"))
