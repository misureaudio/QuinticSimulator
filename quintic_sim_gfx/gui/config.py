"""Persistent GUI configuration (command template + display prefs).

The command template is the heart of the wrapper design: the GUI never
computes anything itself, it substitutes the assembled polynomial into
``{poly}`` and runs the resulting command in a subprocess. The template is
user-editable at runtime (see app.py) and persisted as JSON under the
standard per-user config location, so a different interpreter / package
copy / flag set can be used without touching code.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

APP_NAME = "quintic_sim_gfx"

DEFAULTS = {
    # {poly} is replaced with the assembled polynomial (shell-quoted).
    "command": ".venv/Scripts/python -m quintic_sim {poly} --sage",
    "sage": True,
    "timeout": 300,  # seconds for the subprocess (Sage cross-check can be slow)
    "font_size": 10,
}

# Keys accepted from a persisted file (others are ignored).
_KNOWN = tuple(DEFAULTS)


def config_dir() -> Path:
    """Per-user config directory (overridable in tests via monkeypatch)."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif os.environ.get("XDG_CONFIG_HOME"):
        base = Path(os.environ["XDG_CONFIG_HOME"])
    else:
        base = Path.home() / ".config"
    return base / APP_NAME


def config_path() -> Path:
    return config_dir() / "config.json"


def load() -> dict:
    """Load config, merging a possibly partial/corrupt file over DEFAULTS."""
    p = config_path()
    data = {}
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                data = {}
        except (json.JSONDecodeError, OSError):
            data = {}
    merged = dict(DEFAULTS)
    merged.update({k: v for k, v in data.items() if k in _KNOWN})
    return merged


def save(cfg: dict) -> None:
    d = config_dir()
    d.mkdir(parents=True, exist_ok=True)
    p = config_path()
    p.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
