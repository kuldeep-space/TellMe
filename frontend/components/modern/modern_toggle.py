from PySide6.QtWidgets import QCheckBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from frontend.engine import StyleEngine

class ModernToggle(QCheckBox):
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setObjectName("ModernToggle")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
