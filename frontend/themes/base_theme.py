"""
Theme Engine — Base Theme Protocol & Token System.

Defines:
    - All 14 ThemeToken dataclasses
    - ThemeTokens container
    - ThemeManifest (parsed from manifest.json)
    - AbstractBaseTheme protocol
    - ButtonVariant, BadgeLevel, LabelRole enums (shared across all themes)
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication
    from frontend.engine.style_engine import StyleEngine
    from frontend.themes.component_factory import ComponentFactory


# ══════════════════════════════════════════════════════════════════════════════
# Shared Enums (theme-independent — screens import these)
# ══════════════════════════════════════════════════════════════════════════════

class ButtonVariant(Enum):
    PRIMARY   = "primary"
    SECONDARY = "secondary"
    DANGER    = "danger"
    WARNING   = "warning"
    GHOST     = "ghost"


class BadgeLevel(Enum):
    OK      = "OK"
    ERR     = "ERR"
    WARN    = "WARN"
    INFO    = "INFO"
    BUSY    = "BUSY"
    OFFLINE = "OFFLINE"


class LabelRole(Enum):
    PRIMARY   = "primary"
    SECONDARY = "secondary"
    MUTED     = "muted"
    DANGER    = "danger"
    SUCCESS   = "success"
    WARNING   = "warning"
    H1        = "h1"
    H2        = "h2"


# ══════════════════════════════════════════════════════════════════════════════
# Shadow Configuration
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ShadowConfig:
    """
    Represents a complete shadow definition for one elevation level.
    Supports neumorphic dual-shadow (dark + light) and inset variants.
    """
    dark_x:       int   = 4
    dark_y:       int   = 4
    dark_blur:    int   = 8
    dark_color:   str   = "#00000040"
    light_x:      int   = -4
    light_y:      int   = -4
    light_blur:   int   = 8
    light_color:  str   = "#ffffff80"
    inset:        bool  = False       # True for pressed / recessed states
    glow_color:   str   = ""          # non-empty enables glow ring
    glow_radius:  int   = 8


@dataclass
class ElevationConfig:
    """Maps an elevation level to its shadow + z-order concept."""
    level:  int          = 0
    shadow: ShadowConfig = field(default_factory=ShadowConfig)
    label:  str          = "surface"  # human-readable ("chassis", "panel", "floating")


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 1 — Colors
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ColorTokens:
    background:       str = "#000000"
    surface:          str = "#111111"
    surface_elevated: str = "#1a1a1a"
    surface_hover:    str = "#0d0d0d"
    muted:            str = "#222222"
    text_primary:     str = "#ffffff"
    text_secondary:   str = "#cccccc"
    text_muted:       str = "#888888"
    text_disabled:    str = "#444444"
    text_inverse:     str = "#000000"
    accent:           str = "#ffffff"
    accent_dim:       str = "#cccccc"
    accent_hover:     str = "#ffffff"
    accent_fg:        str = "#000000"
    border:           str = "#333333"
    border_light:     str = "#555555"
    border_dark:      str = "#111111"
    selection:        str = "#333333"


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 2 — Typography
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class TypographyTokens:
    family_sans:      str = "Segoe UI, Arial, sans-serif"
    family_mono:      str = "Consolas, Courier New, monospace"
    family_full_sans: str = "Segoe UI, Arial, sans-serif"
    family_full_mono: str = "Consolas, Courier New, monospace"
    # Sizes in points
    size_xs:   int = 9
    size_sm:   int = 10
    size_base: int = 12
    size_lg:   int = 14
    size_xl:   int = 16
    size_2xl:  int = 18
    size_3xl:  int = 24
    # Weights
    weight_regular:  int = 400
    weight_medium:   int = 500
    weight_semibold: int = 600
    weight_bold:     int = 700
    weight_black:    int = 900
    # Line heights (multipliers)
    line_height_tight:   float = 1.2
    line_height_normal:  float = 1.5
    line_height_relaxed: float = 1.75


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 3 — Spacing
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class SpacingTokens:
    px2:  int = 2
    px4:  int = 4
    px8:  int = 8
    px12: int = 12
    px16: int = 16
    px20: int = 20
    px24: int = 24
    px32: int = 32
    px40: int = 40
    px48: int = 48
    px64: int = 64
    px96: int = 96


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 4 — Radius
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class RadiusTokens:
    none: int = 0
    sm:   int = 4
    md:   int = 8
    lg:   int = 12
    xl:   int = 16
    xxl:  int = 24
    full: int = 9999


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 5 — Shadows
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ShadowTokens:
    card:     ShadowConfig = field(default_factory=lambda: ShadowConfig(
        dark_x=4, dark_y=4, dark_blur=8, dark_color="#00000040",
        light_x=-2, light_y=-2, light_blur=4, light_color="#ffffff20",
    ))
    floating: ShadowConfig = field(default_factory=lambda: ShadowConfig(
        dark_x=8, dark_y=8, dark_blur=16, dark_color="#00000060",
        light_x=-4, light_y=-4, light_blur=8, light_color="#ffffff30",
    ))
    pressed:  ShadowConfig = field(default_factory=lambda: ShadowConfig(
        dark_x=2, dark_y=2, dark_blur=6, dark_color="#00000050",
        light_x=-1, light_y=-1, light_blur=3, light_color="#ffffff20",
        inset=True,
    ))
    recessed: ShadowConfig = field(default_factory=lambda: ShadowConfig(
        dark_x=2, dark_y=2, dark_blur=4, dark_color="#00000040",
        light_x=-2, light_y=-2, light_blur=4, light_color="#ffffff10",
        inset=True,
    ))
    glow:     ShadowConfig = field(default_factory=lambda: ShadowConfig(
        dark_x=0, dark_y=0, dark_blur=10, glow_color="#ffffff",
        glow_radius=10,
    ))


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 6 — Elevation
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ElevationTokens:
    chassis:  ElevationConfig = field(default_factory=lambda: ElevationConfig(level=0,  label="chassis"))
    panel:    ElevationConfig = field(default_factory=lambda: ElevationConfig(level=1,  label="panel"))
    floating: ElevationConfig = field(default_factory=lambda: ElevationConfig(level=2,  label="floating"))
    recessed: ElevationConfig = field(default_factory=lambda: ElevationConfig(level=-1, label="recessed"))


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 7 — Borders
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class BorderTokens:
    width_thin:   int = 1
    width_medium: int = 2
    width_thick:  int = 4
    style_solid:  str = "solid"
    style_dashed: str = "dashed"
    style_dotted: str = "dotted"


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 8 — Animation
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class AnimationTokens:
    duration_fast:   int = 100   # ms — button press, badge flash
    duration_normal: int = 200   # ms — hover, panel lift
    duration_slow:   int = 400   # ms — theme crossfade, LED pulse cycle / 4
    # QEasingCurve.Type values (int constants, avoids Qt import at token level)
    # InOutSine=17, OutSine=16, OutBounce=31, OutBack=36, Linear=0
    easing_spring:       int = 36   # OutBack  — mechanical spring
    easing_out:          int = 16   # OutSine  — smooth deceleration
    easing_in_out:       int = 17   # InOutSine — balanced
    easing_bounce:       int = 31   # OutBounce — playful overshoot
    easing_linear:       int = 0    # Linear
    led_pulse_period_ms: int = 2000 # full LED pulse cycle


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 9 — Icons
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class IconTokens:
    size_xs:    int = 12
    size_sm:    int = 16
    size_md:    int = 20
    size_lg:    int = 24
    size_xl:    int = 32
    stroke_thin:   float = 1.0
    stroke_normal: float = 1.5
    stroke_bold:   float = 2.0


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 10 — Gradients
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class GradientTokens:
    chassis_noise_alpha:  float = 0.0   # 0 = no noise overlay
    lighting_hotspot_alpha: float = 0.0 # 0 = no radial lighting
    radial_tint_color:    str   = "#ffffff"
    button_top_alpha:     float = 0.08  # subtle top highlight on button face
    button_bottom_alpha:  float = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 11 — Textures
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class TextureTokens:
    noise_tile:      str   = "noise_256.png"
    carbon_tile:     str   = "carbon_256.png"
    noise_opacity:   float = 0.0    # 0 = disabled
    carbon_opacity:  float = 0.0    # 0 = disabled
    noise_enabled:   bool  = False
    carbon_enabled:  bool  = False


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 12 — LED
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class LEDTokens:
    dot_size:       int   = 8      # px diameter of core dot
    glow_radius:    int   = 6      # extra px for glow ring
    pulse_enabled:  bool  = False  # whether LED pulses
    pulse_period_ms: int  = 2000   # full cycle in ms
    online_color:   str   = "#22c55e"   # green
    warn_color:     str   = "#f59e0b"   # amber
    error_color:    str   = "#ef4444"   # red
    info_color:     str   = "#3b82f6"   # blue
    offline_color:  str   = "#6b7280"   # grey


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 13 — Status Colors
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class StatusColorTokens:
    success:  str = "#22c55e"
    warning:  str = "#f59e0b"
    danger:   str = "#ef4444"
    info:     str = "#3b82f6"
    busy:     str = "#6b7280"
    offline:  str = "#374151"


# ══════════════════════════════════════════════════════════════════════════════
# Token Category 14 — Layout
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class LayoutTokens:
    sidebar_width:       int = 220
    toolbar_height:      int = 32
    statusbar_height:    int = 28
    navigation_width:    int = 220
    panel_margin:        int = 12
    window_padding:      int = 0
    content_padding:     int = 12
    section_gap:         int = 8
    grid_gap:            int = 8
    dialog_min_width:    int = 480
    dialog_min_height:   int = 320
    splitter_handle_px:  int = 1
    card_padding:        int = 16
    input_min_height:    int = 32
    button_min_height:   int = 28
    touch_target_min:    int = 44


# ══════════════════════════════════════════════════════════════════════════════
# Master Token Container
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ThemeTokens:
    """
    The complete, canonical set of design tokens for one theme.
    All 14 categories must be populated. Screens never read this directly.
    Only StyleEngine and QSSHydrator consume tokens.
    """
    colors:     ColorTokens     = field(default_factory=ColorTokens)
    typography: TypographyTokens = field(default_factory=TypographyTokens)
    spacing:    SpacingTokens   = field(default_factory=SpacingTokens)
    radius:     RadiusTokens    = field(default_factory=RadiusTokens)
    shadows:    ShadowTokens    = field(default_factory=ShadowTokens)
    elevation:  ElevationTokens = field(default_factory=ElevationTokens)
    borders:    BorderTokens    = field(default_factory=BorderTokens)
    animation:  AnimationTokens = field(default_factory=AnimationTokens)
    icons:      IconTokens      = field(default_factory=IconTokens)
    gradients:  GradientTokens  = field(default_factory=GradientTokens)
    textures:   TextureTokens   = field(default_factory=TextureTokens)
    led:        LEDTokens       = field(default_factory=LEDTokens)
    status:     StatusColorTokens = field(default_factory=StatusColorTokens)
    layout:     LayoutTokens    = field(default_factory=LayoutTokens)


# ══════════════════════════════════════════════════════════════════════════════
# Theme Manifest (parsed from manifest.json)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ThemeManifest:
    id:             str
    name:           str
    author:         str        = "Unknown"
    version:        str        = "0.0.0"
    description:    str        = ""
    supports:       str        = ">=0.1.0"
    is_light_mode:  bool       = False
    preview_image:  str        = "preview.png"
    tags:           list       = field(default_factory=list)
    requires_fonts: list       = field(default_factory=list)
    path:           Path       = field(default_factory=Path)   # directory containing the theme

    @classmethod
    def from_json(cls, json_path: Path) -> "ThemeManifest":
        import json
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            author=data.get("author", "Unknown"),
            version=data.get("version", "0.0.0"),
            description=data.get("description", ""),
            supports=data.get("supports", ">=0.1.0"),
            is_light_mode=data.get("is_light_mode", False),
            preview_image=data.get("preview_image", "preview.png"),
            tags=data.get("tags", []),
            requires_fonts=data.get("requires_fonts", []),
            path=json_path.parent,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Abstract Base Theme
# ══════════════════════════════════════════════════════════════════════════════

class AbstractBaseTheme(ABC):
    """
    Protocol every theme must implement.
    ThemeRegistry discovers themes via this interface.

    Minimal implementation:
        - Populate self.tokens: ThemeTokens
        - Implement get_qss_path() → Path
        - Implement get_component_factory() → ComponentFactory
        - Implement on_apply()

    Optional overrides:
        - on_remove()
        - get_preview_pixmap()
        - update_settings()
        - load_settings()
    """

    def __init__(self):
        self._manifest: ThemeManifest | None = None

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique string identifier, e.g. 'terminal', 'industrial'."""

    @property
    @abstractmethod
    def tokens(self) -> ThemeTokens:
        """The fully-populated ThemeTokens for this theme."""

    @property
    def manifest(self) -> ThemeManifest | None:
        return self._manifest

    @manifest.setter
    def manifest(self, value: ThemeManifest):
        self._manifest = value

    @abstractmethod
    def get_qss_path(self) -> Path:
        """Absolute path to the QSS template file for this theme."""

    @abstractmethod
    def get_factory(self, engine: Any) -> "ComponentFactory":
        """Return the ComponentFactory that creates widgets for this theme."""

    @abstractmethod
    def on_apply(self, app: Any, engine: Any) -> None:
        """
        Called when this theme becomes active.
        Perform font registration, Qt palette setup, etc.
        'app' is QApplication instance; 'engine' is StyleEngine.
        """

    def on_remove(self) -> None:
        """Called when this theme is deactivated. Override for cleanup."""

    def get_preview_pixmap(self) -> Any:
        """
        Return a QPixmap thumbnail (320×200) for use in the Settings → Appearance picker.
        Default: attempts to load preview.png from the theme's directory.
        """
        from PySide6.QtGui import QPixmap
        if self._manifest:
            preview_path = self._manifest.path / self._manifest.preview_image
            if preview_path.exists():
                return QPixmap(str(preview_path))
        return None

    def update_settings(self, **kwargs) -> None:
        """
        Update theme-specific settings fields and persist to disk.
        Override in each theme to handle its own settings dataclass.
        """

    def load_settings(self) -> None:
        """
        Load settings from runtime/theme_settings/<id>.json.
        Override in each theme to restore persisted settings.
        """

    def get_settings_schema(self) -> dict:
        """
        Return a dict describing the theme's configurable options.
        Used by the Settings → Appearance screen to auto-build the settings form.
        Format: {field_name: {type, label, description, default, min, max}}
        """
        return {}
