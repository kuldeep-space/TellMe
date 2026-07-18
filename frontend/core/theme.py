"""
ThemeManager — coordinates the active theme, engine setup, and styling.
"""
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from typing import TYPE_CHECKING, Optional

from frontend.themes import ThemeRegistry
from frontend.engine import StyleEngine, ThemeCache, TokenResolver, QSSHydrator, AnimationManager
from backend.core.logging import get_logger

if TYPE_CHECKING:
    from frontend.themes.base_theme import AbstractBaseTheme

_logger = get_logger(__name__)


class ThemeManager(QObject):
    """
    Manages the active theme, theme switching, and live previews.
    Coordinates StyleEngine, TokenResolver, and QSSHydrator.
    """
    theme_applied   = Signal(str)
    preview_started = Signal(str)
    preview_ended   = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._registry = ThemeRegistry()
        self._cache = ThemeCache()
        
        self._active_theme: Optional['AbstractBaseTheme'] = None
        self._preview_theme_id: str = ""
        self._previous_theme_id: str = ""
        
        self._engine: Optional[StyleEngine] = None
        self._anim: Optional[AnimationManager] = None

    @property
    def active_theme(self) -> 'AbstractBaseTheme':
        if self._active_theme is None:
            raise ValueError("No active theme set.")
        return self._active_theme
        
    def setup_engine(self, engine: StyleEngine, anim: AnimationManager):
        self._engine = engine
        self._anim = anim

    def set_theme(self, theme_id: str, persist: bool = True):
        theme = self._registry.get(theme_id)
        if not theme:
            _logger.error(f"Theme '{theme_id}' not found in registry.")
            return

        app = QApplication.instance()
        if not app:
            _logger.error("No QApplication instance found.")
            return

        self._active_theme = theme
        
        # We need to recreate resolver and engine if theme changes
        resolver = TokenResolver(theme.tokens)
        if self._anim is None:
            self._anim = AnimationManager(resolver)
        if self._engine is None:
            self._engine = StyleEngine(resolver, self._cache, self._anim)
        else:
            self._engine._resolver = resolver

        theme.on_apply(app, self._engine)

        qss_content = self._cache.get_qss(theme_id)
        if not qss_content:
            hydrator = QSSHydrator(resolver)
            qss_content = hydrator.hydrate(theme.get_qss_path())
            self._cache.set_qss(theme_id, qss_content)

        app.setStyleSheet(qss_content)
        _logger.info(f"Applied theme: {theme_id}")
        self.theme_applied.emit(theme_id)
        
        if persist:
            pass

    def preview_theme(self, theme_id: str):
        if self._active_theme:
            self._previous_theme_id = self._active_theme.id
        self._preview_theme_id = theme_id
        self.set_theme(theme_id, persist=False)
        self.preview_started.emit(theme_id)

    def commit_preview(self):
        self._preview_theme_id = ""
        self.preview_ended.emit(self.active_theme.id)

    def cancel_preview(self):
        if self._previous_theme_id and self._preview_theme_id:
            self.set_theme(self._previous_theme_id, persist=False)
        self._preview_theme_id = ""
        self.preview_ended.emit(self.active_theme.id)

    def apply_theme(self, name: str):
        """Backward compatibility alias."""
        theme_id = "terminal" if name == "dark" else name
        self.set_theme(theme_id)
