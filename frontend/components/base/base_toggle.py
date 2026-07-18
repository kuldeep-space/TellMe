"""
BaseToggle — Abstract base for switches/checkboxes.
"""
from PySide6.QtWidgets import QCheckBox
from frontend.engine import StyleEngine

class BaseToggle(QCheckBox):
    def __init__(self, engine: StyleEngine, text: str = "", parent=None):
        super().__init__(text, parent)
        self._engine = engine

    @property
    def engine(self) -> StyleEngine:
        return self._engine
