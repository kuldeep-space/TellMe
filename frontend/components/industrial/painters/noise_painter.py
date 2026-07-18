"""
Noise overlay painter — tiles a noise texture for metallic/matte surface finish.
"""
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import QRect

def draw_noise_overlay(painter: QPainter, rect: QRect, texture: QPixmap, opacity: float):
    """Tiled texture drawing with opacity."""
    if texture.isNull() or opacity <= 0:
        return
        
    painter.save()
    painter.setOpacity(opacity)
    
    # Tile it across the rect
    painter.drawTiledPixmap(rect, texture)
    
    painter.restore()
