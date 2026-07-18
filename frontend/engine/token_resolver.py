"""
TokenResolver — resolves dot-path token names to concrete Python values.

Widgets never call this directly. Only StyleEngine and QSSHydrator consume it.

Usage:
    resolver = TokenResolver(tokens)
    resolver.resolve("colors.accent")          → "#ff4757"
    resolver.resolve("typography.size_base")   → 14
    resolver.resolve("layout.sidebar_width")   → 220
    resolver.resolve("animation.duration_fast")→ 150
"""
from __future__ import annotations
from dataclasses import fields, asdict
from typing import Any
from frontend.themes.base_theme import ThemeTokens
from backend.core.logging import get_logger

_logger = get_logger(__name__)


class TokenResolver:
    """
    Dot-path accessor over a ThemeTokens dataclass tree.

    Supports:
        resolve(path)          → raw Python value
        resolve_color(path)    → str (hex) — asserts the value is a string
        resolve_int(path)      → int       — converts to int
        resolve_float(path)    → float
        resolve_str(path)      → str
        dump()                 → dict[str, Any] — full flat token map
        override(path, value)  → temporarily override a token (live editor)
        reset_override(path)   → remove override, restore theme value
        reset_all_overrides()  → clear all live overrides
    """

    def __init__(self, tokens: ThemeTokens):
        self._tokens   = tokens
        self._flat     = self._flatten(tokens)       # base values
        self._overrides: dict[str, Any] = {}         # live editor overrides

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def resolve(self, path: str) -> Any:
        """Resolve a dot-path to its current value (override wins over base)."""
        if path in self._overrides:
            return self._overrides[path]
        if path in self._flat:
            return self._flat[path]
        _logger.warning(f"TokenResolver: unknown path '{path}'")
        return None

    def resolve_color(self, path: str) -> str:
        v = self.resolve(path)
        if not isinstance(v, str):
            _logger.warning(f"Token '{path}' is not a color string: {v!r}")
            return "#000000"
        return v

    def resolve_int(self, path: str) -> int:
        v = self.resolve(path)
        try:
            return int(v)
        except (TypeError, ValueError):
            _logger.warning(f"Token '{path}' cannot be cast to int: {v!r}")
            return 0

    def resolve_float(self, path: str) -> float:
        v = self.resolve(path)
        try:
            return float(v)
        except (TypeError, ValueError):
            _logger.warning(f"Token '{path}' cannot be cast to float: {v!r}")
            return 0.0

    def resolve_bool(self, path: str) -> bool:
        v = self.resolve(path)
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    def resolve_str(self, path: str) -> str:
        v = self.resolve(path)
        return str(v) if v is not None else ""

    def resolve_qcolor(self, path: str) -> Any:
        """Return a QColor for the color at the given path."""
        from PySide6.QtGui import QColor
        return QColor(self.resolve_color(path))

    # ── Live Token Editor support ─────────────────────────────────────────

    def override(self, path: str, value: Any):
        """Override a token value (does not modify the theme; session-only)."""
        self._overrides[path] = value
        _logger.debug(f"Token override: {path} = {value!r}")

    def reset_override(self, path: str):
        self._overrides.pop(path, None)

    def reset_all_overrides(self):
        self._overrides.clear()
        _logger.debug("All token overrides cleared")

    def has_overrides(self) -> bool:
        return bool(self._overrides)

    # ── Introspection ─────────────────────────────────────────────────────

    def dump(self) -> dict[str, Any]:
        """Return a flat dict of all token paths and their current effective values."""
        result = dict(self._flat)          # base values
        result.update(self._overrides)     # overrides win
        return result

    def dump_category(self, category: str) -> dict[str, Any]:
        """Return all tokens under a category prefix, e.g. 'colors'."""
        prefix = f"{category}."
        return {k: v for k, v in self.dump().items() if k.startswith(prefix)}

    # ── Internal ──────────────────────────────────────────────────────────

    @staticmethod
    def _flatten(tokens: ThemeTokens) -> dict[str, Any]:
        """
        Flatten the nested ThemeTokens dataclass into a dot-path dict.
        e.g. tokens.colors.accent → {"colors.accent": "#ff4757"}
        Nested dataclasses are recursed; non-dataclass values are leaves.
        """
        result = {}
        try:
            from dataclasses import fields as dc_fields, is_dataclass
        except ImportError:
            return result

        def _recurse(obj, prefix: str):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    key = f"{prefix}.{k}" if prefix else k
                    _recurse(v, key)
            elif is_dataclass(obj) and not isinstance(obj, type):
                for f in dc_fields(obj):
                    val = getattr(obj, f.name)
                    key = f"{prefix}.{f.name}" if prefix else f.name
                    _recurse(val, key)
            else:
                result[prefix] = obj

        _recurse(tokens, "")
        return result

    def reload(self, tokens: ThemeTokens):
        """Replace underlying tokens (called on theme switch)."""
        self._tokens = tokens
        self._flat   = self._flatten(tokens)
        # Keep overrides intentionally — user may be live-editing
