"""
BaseButton — Abstract base for push buttons.
"""
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon
from frontend.engine import StyleEngine
from frontend.themes.base_theme import ButtonVariant

class BaseButton(QPushButton):
    """
    Base class for all buttons.
    Defines variant support.
    """
    def __init__(self, engine: StyleEngine, text: str = "", variant: ButtonVariant = ButtonVariant.PRIMARY, parent=None):
        super().__init__(text, parent)
        self._engine = engine
        self._variant = variant
        self.setProperty("variant", variant.value)

    @property
    def variant(self) -> ButtonVariant:
        return self._variant

    @property
    def engine(self) -> StyleEngine:
        return self._engine

    def set_icon(self, name: str, color: str = ""):
        """Helper to resolve icon through theme cache."""
        icon = self._engine.cache.get_icon(name, color)
        if icon:
            self.setIcon(icon)
            
    def set_icon_raw(self, icon: QIcon):
        self.setIcon(icon)
