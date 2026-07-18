"""
LedIndicator — A glowing LED dot for status.
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPaintEvent, QColor, QRadialGradient
from PySide6.QtCore import Qt, QRectF, Property
from frontend.engine import StyleEngine

class LedIndicator(QWidget):
    def __init__(self, engine: StyleEngine, color_token: str = "led.online_color", parent=None):
        super().__init__(parent)
        self._engine = engine
        self._color_token = color_token
        self._alpha = 1.0
        
        dot_size = engine.resolver.resolve_int("led.dot_size")
        glow = engine.resolver.resolve_int("led.glow_radius")
        size = dot_size + glow * 2
        self.setFixedSize(size, size)
        
        if engine.resolver.resolve_bool("led.pulse_enabled"):
            self._pulse = engine.anim.register_led_pulse(self, b"alpha")
            
    @Property(float)
    def alpha(self) -> float:
        return self._alpha
        
    @alpha.setter
    def alpha(self, value: float):
        self._alpha = value
        self.update()
        
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        base_color = self._engine.resolver.resolve_qcolor(self._color_token)
        color = QColor(base_color.red(), base_color.green(), base_color.blue(), int(255 * self._alpha))
        
        rect = QRectF(self.rect())
        center = rect.center()
        dot_size = self._engine.resolver.resolve_int("led.dot_size")
        glow = self._engine.resolver.resolve_int("led.glow_radius")
        
        # Glow
        if glow > 0:
            grad = QRadialGradient(center, dot_size / 2 + glow)
            grad.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 100))
            grad.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, dot_size / 2 + glow, dot_size / 2 + glow)
            
        # Core
        painter.setBrush(color)
        painter.setPen(color.darker(150))
        painter.drawEllipse(center, dot_size / 2, dot_size / 2)
