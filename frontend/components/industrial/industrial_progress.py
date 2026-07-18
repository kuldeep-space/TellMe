"""
IndustrialProgress — Analog segmented progress or continuous recessed bar.
"""
from PySide6.QtGui import QPainter, QPaintEvent, QColor
from PySide6.QtCore import QRectF, Qt
from frontend.components.base.base_progress import BaseProgress
from frontend.engine import StyleEngine
from frontend.components.industrial.painters.neumorphic import draw_inset_shadow

class IndustrialProgress(BaseProgress):
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(engine, parent)
        self.setMinimumHeight(16)
        
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        rect = QRectF(self.rect())
        radius = rect.height() / 2
        
        # Inset track
        bg_color = self.engine.resolver.resolve_qcolor("colors.background")
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)
        
        dark_shadow = QColor(0, 0, 0, 150)
        light_shadow = QColor(255, 255, 255, 20)
        draw_inset_shadow(painter, rect, radius, dark_shadow, light_shadow)
        
        # Fill
        if self.maximum() > 0:
            ratio = self.value() / self.maximum()
            if ratio > 0:
                fill_rect = QRectF(rect.x(), rect.y(), rect.width() * ratio, rect.height())
                # Shrink fill slightly to fit inside the inset
                fill_rect.adjust(2, 2, -2, -2)
                
                fill_color = self.engine.resolver.resolve_qcolor("colors.accent")
                painter.setBrush(fill_color)
                painter.drawRoundedRect(fill_rect, radius - 2, radius - 2)
