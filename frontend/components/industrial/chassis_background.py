"""
ChassisBackground — Root window background.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QPaintEvent, QColor
from PySide6.QtCore import QRectF, Qt
from frontend.engine import StyleEngine
from frontend.components.industrial.painters.screw_painter import draw_screws
from frontend.components.industrial.painters.vent_painter import draw_vents
from frontend.components.industrial.painters.noise_painter import draw_noise_overlay

class ChassisBackground(QWidget):
    """
    Renders the main metallic chassis for the application.
    """
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(parent)
        self._engine = engine
        self.body_layout = QVBoxLayout(self)
        self.body_layout.setContentsMargins(24, 24, 24, 24)
        
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        rect = self.rect()
        
        # Base metal color
        bg = self._engine.resolver.resolve_qcolor("colors.background")
        painter.fillRect(rect, bg)
        
        # Noise texture
        noise_tex = self._engine.cache.get_texture(self._engine.resolver.resolve_str("textures.noise_tile"))
        opacity = self._engine.resolver.resolve_float("textures.noise_opacity")
        if noise_tex and opacity > 0:
            draw_noise_overlay(painter, rect, noise_tex, opacity)
            
        # Large corner screws
        screw_color = bg.darker(150)
        draw_screws(painter, rect.width(), rect.height(), margin=16, size=14, color=screw_color)
        
        # Draw some vents at the top and bottom
        dark = QColor(0, 0, 0, 180)
        light = QColor(255, 255, 255, 30)
        
        # Top vents
        top_vent_rect = QRectF(rect.width() / 2 - 100, 10, 200, 15)
        draw_vents(painter, top_vent_rect, num_vents=10, spacing=4, dark_color=dark, light_color=light, vertical=True)
        
        # Bottom vents
        bottom_vent_rect = QRectF(rect.width() / 2 - 100, rect.height() - 25, 200, 15)
        draw_vents(painter, bottom_vent_rect, num_vents=10, spacing=4, dark_color=dark, light_color=light, vertical=True)
