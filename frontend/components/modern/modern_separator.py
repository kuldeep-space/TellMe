from PySide6.QtWidgets import QFrame
from PySide6.QtCore import Qt
from frontend.engine import StyleEngine

class ModernSeparator(QFrame):
    def __init__(self, engine: StyleEngine, horizontal: bool = True, parent=None):
        super().__init__(parent)
        self.engine = engine
        
        color = engine.resolver.resolve_qcolor("colors.border").name()
        
        if horizontal:
            self.setFixedHeight(1)
            self.setStyleSheet(f"background-color: {color}; opacity: 0.1;")
        else:
            self.setFixedWidth(1)
            self.setStyleSheet(f"background-color: {color}; opacity: 0.1;")
