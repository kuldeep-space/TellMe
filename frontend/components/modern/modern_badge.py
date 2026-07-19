from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from frontend.engine import StyleEngine
from frontend.themes.base_theme import BadgeLevel

class ModernBadge(QWidget):
    def __init__(self, engine: StyleEngine, text: str, level: BadgeLevel = BadgeLevel.INFO, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._level = level
        self.setObjectName("ModernBadge")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        self._lbl = QLabel(text.upper())
        self._lbl.setObjectName(f"ModernBadgeText_{level.name}")
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._lbl)

    def set_level(self, level: BadgeLevel):
        """Update the badge level and re-style it."""
        self._level = level
        self._lbl.setText(level.value.upper())
        self._lbl.setObjectName(f"ModernBadgeText_{level.name}")
        # Force QSS re-polish so theme-driven colors update
        self._lbl.style().unpolish(self._lbl)
        self._lbl.style().polish(self._lbl)
        self._lbl.update()

