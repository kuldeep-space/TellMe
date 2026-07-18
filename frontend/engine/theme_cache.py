"""
ThemeCache — centralized cache for all expensive theme assets.

Caches: fonts (registration status), icons, textures, QPixmaps, gradients,
and hydrated QSS strings (keyed by theme_id).

Theme switching costs zero re-generation when switching back to a previously-
activated theme. Call invalidate_theme(theme_id) when token values change
(e.g. from the Live Token Editor).
"""
from __future__ import annotations
from typing import Any
from backend.core.logging import get_logger

_logger = get_logger(__name__)


class ThemeCache:
    """
    Singleton asset cache. All values stored by string keys.

    API:
        get_font(family) → bool
        set_font(family, registered)
        get_icon(name, color) → QIcon | None
        set_icon(name, color, icon)
        get_texture(name) → QPixmap | None
        set_texture(name, pixmap)
        get_gradient(key) → QGradient | None
        set_gradient(key, gradient)
        get_qss(theme_id) → str | None
        set_qss(theme_id, qss)
        invalidate_theme(theme_id) → clears qss cache for that theme
        clear_all()
    """

    _instance: "ThemeCache | None" = None

    def __new__(cls) -> "ThemeCache":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_caches()
        return cls._instance

    def _init_caches(self):
        self._fonts:     dict[str, bool]  = {}
        self._icons:     dict[str, Any]   = {}   # QIcon
        self._textures:  dict[str, Any]   = {}   # QPixmap
        self._gradients: dict[str, Any]   = {}   # QGradient
        self._qss:       dict[str, str]   = {}   # hydrated QSS per theme_id
        self._hits   = 0
        self._misses = 0

    # ── Font ──────────────────────────────────────────────────────────────
    def get_font(self, family: str) -> bool | None:
        return self._fonts.get(family)

    def set_font(self, family: str, registered: bool):
        self._fonts[family] = registered

    # ── Icons ─────────────────────────────────────────────────────────────
    def _icon_key(self, name: str, color: str) -> str:
        return f"{name}::{color}"

    def get_icon(self, name: str, color: str = "") -> Any | None:
        key = self._icon_key(name, color)
        if key in self._icons:
            self._hits += 1
            return self._icons[key]
        self._misses += 1
        return None

    def set_icon(self, name: str, color: str, icon: Any):
        self._icons[self._icon_key(name, color)] = icon

    # ── Textures ──────────────────────────────────────────────────────────
    def get_texture(self, name: str) -> Any | None:
        if name in self._textures:
            self._hits += 1
            return self._textures[name]
        self._misses += 1
        return None

    def set_texture(self, name: str, pixmap: Any):
        self._textures[name] = pixmap

    # ── Gradients ─────────────────────────────────────────────────────────
    def get_gradient(self, key: str) -> Any | None:
        if key in self._gradients:
            self._hits += 1
            return self._gradients[key]
        self._misses += 1
        return None

    def set_gradient(self, key: str, gradient: Any):
        self._gradients[key] = gradient

    # ── QSS ───────────────────────────────────────────────────────────────
    def get_qss(self, theme_id: str) -> str | None:
        if theme_id in self._qss:
            self._hits += 1
            return self._qss[theme_id]
        self._misses += 1
        return None

    def set_qss(self, theme_id: str, qss: str):
        self._qss[theme_id] = qss
        _logger.debug(f"ThemeCache: QSS cached for theme '{theme_id}' ({len(qss):,} chars)")

    # ── Invalidation ──────────────────────────────────────────────────────
    def invalidate_theme(self, theme_id: str):
        """Remove cached QSS for a theme (forces re-hydration next activation)."""
        removed = self._qss.pop(theme_id, None)
        if removed is not None:
            _logger.debug(f"ThemeCache: QSS invalidated for theme '{theme_id}'")

    def clear_all(self):
        """Full cache reset — called on app exit or major error recovery."""
        self._init_caches()
        _logger.debug("ThemeCache: all caches cleared")

    # ── Stats ─────────────────────────────────────────────────────────────
    def stats(self) -> dict:
        return {"hits": self._hits, "misses": self._misses, "qss_cached": list(self._qss.keys())}
