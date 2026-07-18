"""
BaseProgress — Abstract base for progress bars.
"""
from PySide6.QtWidgets import QProgressBar
from frontend.engine import StyleEngine

class BaseProgress(QProgressBar):
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(parent)
        self._engine = engine
        self.setTextVisible(False)
        
    def set_value(self, val: int):
        self.setValue(val)
        
    @property
    def engine(self) -> StyleEngine:
        return self._engine
