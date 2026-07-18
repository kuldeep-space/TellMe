from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from frontend.engine import StyleEngine

class ModernStatusBar(QWidget):
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setFixedHeight(32)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        
        self.status_lbl = QLabel("READY")
        self.status_lbl.setObjectName("ModernStatusLabel")
        self.status_lbl.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(self.status_lbl)
        layout.addStretch()

    def set_status(self, text: str):
        self.status_lbl.setText(text)
