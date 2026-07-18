"""
BaseSidebar — Abstract base for the main navigation sidebar.
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from frontend.engine import StyleEngine

class BaseSidebar(QWidget):
    navigation_requested = Signal(str)

    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(parent)
        self._engine = engine

    @property
    def engine(self) -> StyleEngine:
        return self._engine
