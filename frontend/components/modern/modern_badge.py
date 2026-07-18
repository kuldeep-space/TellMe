from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from frontend.engine import StyleEngine
from frontend.themes.base_theme import BadgeLevel

class ModernBadge(QWidget):
    def __init__(self, engine: StyleEngine, text: str, level: BadgeLevel = BadgeLevel.INFO, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setObjectName("ModernBadge")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        lbl = QLabel(text.upper())
        lbl.setObjectName(f"ModernBadgeText_{level.name}")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
