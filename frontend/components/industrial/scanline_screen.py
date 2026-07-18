"""
ScanlineScreen — Glass/CRT overlay for terminal areas inside the industrial chassis.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QPaintEvent, QColor
from PySide6.QtCore import Qt, QRectF
from frontend.engine import StyleEngine
from frontend.components.industrial.painters.neumorphic import draw_inset_shadow

class ScanlineScreen(QWidget):
    """
    A recessed screen area that renders a dark background with CRT/Scanline effects.
    """
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(parent)
        self._engine = engine
        self.body_layout = QVBoxLayout(self)
        self.body_layout.setContentsMargins(12, 12, 12, 12)
        
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        rect = QRectF(self.rect())
        radius = 8.0
        
        # Dark glass background
        painter.setBrush(QColor(10, 15, 10))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)
        
        # Scanlines (simple horizontal lines)
        painter.setPen(QColor(0, 255, 0, 5))
        for y in range(0, int(rect.height()), 3):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            
        # Inset shadow (screen bezel)
        dark = QColor(0, 0, 0, 200)
        light = QColor(255, 255, 255, 40)
        draw_inset_shadow(painter, rect, radius, dark, light)
