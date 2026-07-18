"""
BaseBadge — Abstract base for status badges.
"""
from PySide6.QtWidgets import QLabel
from frontend.engine import StyleEngine
from frontend.themes.base_theme import BadgeLevel

class BaseBadge(QLabel):
    """
    Base class for status indicator badges.
    """
    def __init__(self, engine: StyleEngine, text: str = "", level: BadgeLevel = BadgeLevel.INFO, parent=None):
        super().__init__(text, parent)
        self._engine = engine
        self.set_level(level)

    def set_level(self, level: BadgeLevel):
        self._level = level
        self.setProperty("level", level.value)
        self.style().unpolish(self)
        self.style().polish(self)

    @property
    def engine(self) -> StyleEngine:
        return self._engine
