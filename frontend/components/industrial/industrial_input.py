"""
IndustrialInput — Recessed input field.
"""
from PySide6.QtGui import QPainter, QPaintEvent, QColor
from PySide6.QtCore import QRectF, Qt
from frontend.components.base.base_input import BaseInput
from frontend.engine import StyleEngine
from frontend.components.industrial.painters.neumorphic import draw_inset_shadow

class IndustrialInput(BaseInput):
    def __init__(self, engine: StyleEngine, placeholder: str = "", parent=None):
        super().__init__(engine, placeholder, parent)
        self.setMinimumHeight(engine.resolver.resolve_int("layout.input_min_height"))
        # Frame drawing is handled by QSS or custom paint, we will use QSS mostly for inputs,
        # but can do custom paint for inset shadow
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def paintEvent(self, event: QPaintEvent):
        # We need to paint the inset shadow before letting QLineEdit paint its text
        painter = QPainter(self)
        rect = QRectF(self.rect())
        radius = self.engine.resolver.resolve_int("radius.sm")
        
        dark_shadow = QColor(0, 0, 0, 150)
        light_shadow = QColor(255, 255, 255, 20)
        
        painter.setBrush(self.engine.resolver.resolve_qcolor("colors.background"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)
        
        draw_inset_shadow(painter, rect, radius, dark_shadow, light_shadow)
        
        # Now let QLineEdit paint the text over it
        super().paintEvent(event)
