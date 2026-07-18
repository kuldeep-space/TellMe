"""
IndustrialSeparator — Engraved groove line.
"""
from PySide6.QtGui import QPainter, QPaintEvent, QColor
from PySide6.QtCore import QRectF, Qt
from frontend.components.base.base_separator import BaseSeparator
from frontend.engine import StyleEngine

class IndustrialSeparator(BaseSeparator):
    def __init__(self, engine: StyleEngine, horizontal: bool = True, parent=None):
        super().__init__(engine, horizontal, parent)
        if horizontal:
            self.setFixedHeight(2)
        else:
            self.setFixedWidth(2)
            
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        rect = self.rect()
        
        dark = QColor(0, 0, 0, 150)
        light = QColor(255, 255, 255, 20)
        
        if self.property("horizontal"):
            painter.setPen(dark)
            painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
            painter.setPen(light)
            painter.drawLine(rect.left(), rect.top() + 1, rect.right(), rect.top() + 1)
        else:
            painter.setPen(dark)
            painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())
            painter.setPen(light)
            painter.drawLine(rect.left() + 1, rect.top(), rect.left() + 1, rect.bottom())
