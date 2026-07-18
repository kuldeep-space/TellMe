"""
SteelPanel — A base panel with neumorphic rendering and optional screws/vents.
"""
from PySide6.QtGui import QPainter, QPaintEvent, QColor
from PySide6.QtCore import QRectF, Qt
from frontend.components.base.base_panel import BasePanel
from frontend.engine import StyleEngine
from frontend.components.industrial.painters.neumorphic import draw_neumorphic_panel
from frontend.components.industrial.painters.screw_painter import draw_screws
from frontend.components.industrial.painters.noise_painter import draw_noise_overlay

class SteelPanel(BasePanel):
    def __init__(self, engine: StyleEngine, elevation: str = "panel", parent=None,
                 screws: bool = False, vents: bool = False):
        super().__init__(engine, elevation, parent)
        self._screws = screws
        self._vents = vents
        
        from PySide6.QtWidgets import QVBoxLayout
        self.body_layout = QVBoxLayout(self)
        self.body_layout.setContentsMargins(16, 16, 16, 16)
        self.body_layout.setSpacing(8)
        
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        rect = QRectF(self.rect())
        
        radius = 5
        bg_color = self.engine.resolver.resolve_qcolor("colors.surface")
        border_color = self.engine.resolver.resolve_qcolor("colors.border")
        
        # Resolve shadows from elevation (e.g., shadows.card or shadows.floating)
        # simplified for steel panel
        dark_shadow = QColor(0, 0, 0, 100)
        light_shadow = QColor(255, 255, 255, 20)
        
        draw_neumorphic_panel(painter, rect, radius, bg_color, dark_shadow, light_shadow)
        
        # Clean border
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QColor(border_color))
        painter.drawRoundedRect(rect, radius, radius)
        
        noise_tex = self.engine.cache.get_texture(self.engine.resolver.resolve_str("textures.noise_tile"))
        opacity = self.engine.resolver.resolve_float("textures.noise_opacity")
        if noise_tex and opacity > 0:
            draw_noise_overlay(painter, self.rect(), noise_tex, opacity)
            
        if self._screws:
            screw_color = bg_color.darker(150)
            draw_screws(painter, self.width(), self.height(), margin=12, size=10, color=screw_color)
            
        super().paintEvent(event)
