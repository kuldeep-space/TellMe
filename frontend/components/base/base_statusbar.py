"""
BaseStatusbar — Abstract base for the main status bar.
"""
from PySide6.QtWidgets import QStatusBar
from frontend.engine import StyleEngine

class BaseStatusbar(QStatusBar):
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(parent)
        self._engine = engine
        # Many themes will paint a custom background

    @property
    def engine(self) -> StyleEngine:
        return self._engine
