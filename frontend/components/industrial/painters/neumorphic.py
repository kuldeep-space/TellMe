"""
Neumorphic rendering utilities.
"""
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen
from PySide6.QtCore import QRectF, Qt

def draw_neumorphic_panel(painter: QPainter, rect: QRectF, radius: float, 
                          bg_color: QColor, dark_shadow: QColor, light_shadow: QColor):
    """
    Draws a rounded rect with drop shadows representing a raised surface.
    In standard Qt without QGraphicsDropShadowEffect (which is expensive and limited to one),
    we draw the shadows manually using multiple passes or simplified offset drawing.
    """
    # Simple simulated drop shadow
    # For a real implementation, we'd render the shadows into a pixmap and blur them,
    # or use a 9-patch image. Here we do a fast multi-pass offset.
    
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Dark shadow (bottom right)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(dark_shadow)
    painter.drawRoundedRect(rect.translated(4, 4), radius, radius)
    
    # Light shadow (top left)
    painter.setBrush(light_shadow)
    painter.drawRoundedRect(rect.translated(-2, -2), radius, radius)
    
    # Main surface
    painter.setBrush(bg_color)
    painter.drawRoundedRect(rect, radius, radius)
    
    painter.restore()

def draw_inset_shadow(painter: QPainter, rect: QRectF, radius: float,
                      dark_shadow: QColor, light_shadow: QColor):
    """
    Draws an inner shadow for recessed elements like pressed buttons or input fields.
    """
    from PySide6.QtCore import Qt
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Simple inset simulation using pens
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)
    
    # Clip to the rounded rect
    painter.setClipPath(path)
    
    # Dark shadow top-left
    pen = QPen(dark_shadow, 3)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(rect.adjusted(-1, -1, 1, 1).translated(2, 2), radius, radius)
    
    # Light shadow bottom-right
    pen = QPen(light_shadow, 3)
    painter.setPen(pen)
    painter.drawRoundedRect(rect.adjusted(-1, -1, 1, 1).translated(-2, -2), radius, radius)
    
    painter.restore()
