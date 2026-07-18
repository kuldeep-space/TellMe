"""
Terminal Theme — AbstractBaseTheme implementation.

Wraps the existing terminal aesthetic as a first-class theme package.
The visual output is byte-for-byte identical to the pre-migration app.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any

from frontend.themes.base_theme import AbstractBaseTheme, ThemeTokens, ThemeManifest
from frontend.themes.builtin.terminal.tokens import make_terminal_tokens
from frontend.themes.builtin.terminal.settings import TerminalThemeSettings
from backend.core.logging import get_logger

_logger = get_logger(__name__)
_THEME_DIR = Path(__file__).parent


class TerminalTheme(AbstractBaseTheme):
    """
    The original TellMe Terminal theme.

    Aesthetic: Dark phosphor-green CRT terminal.
    Mode: Dark
    Fonts: JetBrains Mono (mono-only, no sans-serif)
    Radius: Zero (hard edges everywhere)
    Animations: Minimal (no spring physics, no neumorphic shadows)
    """

    def __init__(self):
        super().__init__()
        self._tokens:   ThemeTokens           = make_terminal_tokens()
        self._settings: TerminalThemeSettings = TerminalThemeSettings()

    # ------------------------------------------------------------------ #
    # AbstractBaseTheme Interface
    # ------------------------------------------------------------------ #

    @property
    def id(self) -> str:
        return "terminal"

    @property
    def tokens(self) -> ThemeTokens:
        return self._tokens

    @property
    def settings(self) -> TerminalThemeSettings:
        return self._settings

    def get_qss_path(self) -> Path:
        return _THEME_DIR / "style.qss"

    def get_factory(self, engine: Any) -> Any:
        from frontend.themes.builtin.terminal.factory import TerminalComponentFactory
        return TerminalComponentFactory(engine)

    def on_apply(self, app: Any, engine: Any) -> None:
        """
        Activating the Terminal theme:
        1. Set Qt dark palette (black background, green text)
        2. Ensure JetBrains Mono is the application-wide default font
        """
        from PySide6.QtGui import QPalette, QColor, QFont
        from PySide6.QtWidgets import QApplication

        palette = QPalette()
        bg = QColor(self._tokens.colors.background)
        fg = QColor(self._tokens.colors.text_primary)
        palette.setColor(QPalette.ColorRole.Window,          bg)
        palette.setColor(QPalette.ColorRole.WindowText,      fg)
        palette.setColor(QPalette.ColorRole.Base,            QColor(self._tokens.colors.surface))
        palette.setColor(QPalette.ColorRole.Text,            fg)
        palette.setColor(QPalette.ColorRole.Button,          bg)
        palette.setColor(QPalette.ColorRole.ButtonText,      fg)
        palette.setColor(QPalette.ColorRole.Highlight,       QColor(self._tokens.colors.selection))
        palette.setColor(QPalette.ColorRole.HighlightedText, fg)
        if isinstance(app, QApplication):
            app.setPalette(palette)

        font = QFont(self._tokens.typography.family_mono, self._tokens.typography.size_base)
        if isinstance(app, QApplication):
            app.setFont(font)

        _logger.info("Terminal theme applied: dark palette + JetBrains Mono")

    def on_remove(self) -> None:
        _logger.debug("Terminal theme deactivated")

    # ------------------------------------------------------------------ #
    # Settings
    # ------------------------------------------------------------------ #

    def update_settings(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if hasattr(self._settings, k) and k != "SCHEMA":
                setattr(self._settings, k, v)

    def load_settings(self) -> None:
        from backend.config.settings import get_settings
        settings_dir = get_settings().runtime_path / "theme_settings"
        self._settings = TerminalThemeSettings.load(settings_dir)

    def get_settings_schema(self) -> dict:
        return self._settings.SCHEMA


# ── Module-level singleton (loaded once by ThemeRegistry) ───────────────────
_instance: TerminalTheme | None = None


def get_theme() -> TerminalTheme:
    """Return the module-level TerminalTheme singleton."""
    global _instance
    if _instance is None:
        _instance = TerminalTheme()
    return _instance
