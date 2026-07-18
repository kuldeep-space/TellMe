"""
Terminal Theme Settings — configurable per-user options for the Terminal theme.
Persisted to runtime/theme_settings/terminal.json.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path
from backend.core.logging import get_logger

_logger = get_logger(__name__)


@dataclass
class TerminalThemeSettings:
    """
    All configurable options exposed by the Terminal theme.
    Values are applied via StyleEngine on theme activation and on setting change.
    """
    crt_scanlines:   bool  = True    # Enable CRT scanline overlay
    crt_vignette:    bool  = True    # Enable edge vignette darkening
    crt_flicker:     bool  = False   # Enable subtle phosphor flicker animation
    font_size_base:  int   = 12      # Base font size in points
    sidebar_width:   int   = 220     # Sidebar width in pixels
    cursor_blink:    bool  = True    # Cursor blink in text areas
    reduce_motion:   bool  = False   # Disable all animations

    SCHEMA: dict = field(default_factory=lambda: {
        "crt_scanlines":  {"type": "bool",  "label": "CRT Scanlines",         "description": "Enable horizontal scanline overlay"},
        "crt_vignette":   {"type": "bool",  "label": "Edge Vignette",          "description": "Darken screen edges"},
        "crt_flicker":    {"type": "bool",  "label": "Phosphor Flicker",       "description": "Subtle screen flicker effect"},
        "font_size_base": {"type": "int",   "label": "Base Font Size (pt)",    "description": "Base monospace font size", "min": 8, "max": 20},
        "sidebar_width":  {"type": "int",   "label": "Sidebar Width (px)",     "description": "Width of navigation sidebar", "min": 160, "max": 320},
        "cursor_blink":   {"type": "bool",  "label": "Cursor Blink",           "description": "Blinking cursor in text fields"},
        "reduce_motion":  {"type": "bool",  "label": "Reduce Motion",          "description": "Disable all animations"},
    })

    def save(self, settings_dir: Path):
        settings_dir.mkdir(parents=True, exist_ok=True)
        path = settings_dir / "terminal.json"
        data = {k: v for k, v in asdict(self).items() if k != "SCHEMA"}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        _logger.debug(f"Terminal settings saved: {path}")

    @classmethod
    def load(cls, settings_dir: Path) -> "TerminalThemeSettings":
        path = settings_dir / "terminal.json"
        if not path.exists():
            return cls()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            inst = cls()
            for k, v in data.items():
                if hasattr(inst, k) and k != "SCHEMA":
                    setattr(inst, k, v)
            return inst
        except Exception as e:
            _logger.warning(f"Terminal settings load failed ({e}); using defaults")
            return cls()
