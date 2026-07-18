"""
BaseSeparator — Abstract base for visual dividers.
"""
from PySide6.QtWidgets import QFrame
from frontend.engine import StyleEngine

class BaseSeparator(QFrame):
    def __init__(self, engine: StyleEngine, horizontal: bool = True, parent=None):
        super().__init__(parent)
        self._engine = engine
        self.setProperty("horizontal", horizontal)
        if horizontal:
            self.setFrameShape(QFrame.Shape.HLine)
            self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Plain)

    @property
    def engine(self) -> StyleEngine:
        return self._engine
