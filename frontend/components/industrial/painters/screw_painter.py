"""
Screw painter — draws industrial Phillips or Torx screws in panel corners.
"""
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QPointF, QRectF
import math

def draw_screws(painter: QPainter, width: int, height: int, margin: int, size: int, color: QColor):
    """Draws 4 screws in the corners of a rectangle."""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    positions = [
        QPointF(margin, margin),
        QPointF(width - margin, margin),
        QPointF(margin, height - margin),
        QPointF(width - margin, height - margin)
    ]
    
    painter.setBrush(color.darker(120))
    pen = QPen(color.darker(150), 1)
    painter.setPen(pen)
    
    for i, pos in enumerate(positions):
        # Base circle
        painter.drawEllipse(pos, size, size)
        
        # Inner shadow for depth
        shadow_rect = QRectF(pos.x() - size + 1, pos.y() - size + 1, (size - 1) * 2, (size - 1) * 2)
        
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Top-left dark inner shadow
        painter.setPen(QPen(QColor(0, 0, 0, 180), 1.5))
        painter.drawArc(shadow_rect, 45 * 16, 180 * 16)
        
        # Bottom-right light inner shadow
        painter.setPen(QPen(QColor(255, 255, 255, 80), 1.5))
        painter.drawArc(shadow_rect, 225 * 16, 180 * 16)
        
        # Phillips cross slot (slightly rotated per screw for realism)
        angle = (i * 35) % 90
        painter.translate(pos)
        painter.rotate(angle)
        
        # Dark slot lines
        slot_pen = QPen(QColor(10, 10, 10, 200), 1.5)
        painter.setPen(slot_pen)
        radius = size * 0.7
        painter.drawLine(QPointF(-radius, 0), QPointF(radius, 0))
        painter.drawLine(QPointF(0, -radius), QPointF(0, radius))
        
        painter.rotate(-angle)
        painter.translate(-pos)

    painter.restore()
