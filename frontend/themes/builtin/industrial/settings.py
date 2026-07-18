"""
Industrial Settings — Theme Settings panel.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class IndustrialSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Industrial Theme Settings\n(No configurable options yet)"))
        layout.addStretch()
