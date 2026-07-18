from PySide6.QtWidgets import QProgressBar
from frontend.engine import StyleEngine

class ModernProgress(QProgressBar):
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setObjectName("ModernProgress")
        self.setTextVisible(False)
        self.setFixedHeight(8)

    def set_value(self, val: int):
        self.setValue(val)
