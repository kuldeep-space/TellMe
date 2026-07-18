from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit
from PySide6.QtCore import Qt

class TextInput(QWidget):
    def __init__(self, label_text, placeholder="", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        self.label = QLabel(label_text)
        self.label.setStyleSheet("font-size: 14px; font-weight: 500;")
        
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setObjectName("textInput")
        self.input.setMinimumHeight(44)
        
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        
    def text(self):
        return self.input.text()
        
    def set_text(self, text):
        self.input.setText(text)
