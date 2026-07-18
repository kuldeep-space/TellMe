"""
BaseInput — Abstract base for line edits.
"""
from PySide6.QtWidgets import QLineEdit
from frontend.engine import StyleEngine

class BaseInput(QLineEdit):
    """
    Base class for text input fields.
    """
    def __init__(self, engine: StyleEngine, placeholder: str = "", parent=None):
        super().__init__(parent)
        self._engine = engine
        if placeholder:
            self.setPlaceholderText(placeholder)

    def set_invalid(self, invalid: bool):
        self.setProperty("invalid", invalid)
        self.style().unpolish(self)
        self.style().polish(self)

    @property
    def engine(self) -> StyleEngine:
        return self._engine
