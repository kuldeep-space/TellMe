
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

class PrimaryButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("primaryButton")

class SecondaryButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("secondaryButton")

class IconButton(QPushButton):
    def __init__(self, icon, parent=None):
        super().__init__(parent)
        self.setIcon(icon)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("iconButton")

