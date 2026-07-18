"""
IndustrialToggle — A physical rocker switch or slider.
"""
from PySide6.QtGui import QPainter, QPaintEvent, QColor
from PySide6.QtCore import QRectF, Qt
from frontend.components.base.base_toggle import BaseToggle
from frontend.engine import StyleEngine
from frontend.components.industrial.painters.neumorphic import draw_neumorphic_panel, draw_inset_shadow

class IndustrialToggle(BaseToggle):
    def __init__(self, engine: StyleEngine, label: str = "", parent=None):
        super().__init__(engine, label, parent)
        self.setFixedSize(60, 30)
        # Disable native checkbox rendering
        self.setStyleSheet("QCheckBox::indicator { width: 0; height: 0; }")
        
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        rect = QRectF(self.rect())
        radius = rect.height() / 2
        
        # Track (recessed)
        painter.setBrush(self.engine.resolver.resolve_qcolor("colors.background"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)
        
        dark_shadow = QColor(0, 0, 0, 150)
        light_shadow = QColor(255, 255, 255, 20)
        draw_inset_shadow(painter, rect, radius, dark_shadow, light_shadow)
        
        # Knob (raised)
        knob_size = rect.height() - 4
        if self.isChecked():
            knob_x = rect.width() - knob_size - 2
            knob_color = self.engine.resolver.resolve_qcolor("colors.accent")
        else:
            knob_x = 2
            knob_color = self.engine.resolver.resolve_qcolor("colors.surface")
            
        knob_rect = QRectF(knob_x, 2, knob_size, knob_size)
        draw_neumorphic_panel(painter, knob_rect, knob_size / 2, knob_color, dark_shadow, light_shadow)
        
        # We don't draw text on the toggle itself in industrial, rely on external labels
