"""
Vent painter — draws ventilation grilles.
"""
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QRectF

def draw_vents(painter: QPainter, rect: QRectF, num_vents: int, spacing: int, 
               dark_color: QColor, light_color: QColor, vertical: bool = True):
    """Draws a series of ventilation slots (recessed lines)."""
    painter.save()
    
    start_x = rect.x()
    start_y = rect.y()
    
    if vertical:
        slot_width = 3
        slot_height = rect.height()
        total_width = num_vents * slot_width + (num_vents - 1) * spacing
        offset_x = start_x + (rect.width() - total_width) / 2
        
        for i in range(num_vents):
            x = offset_x + i * (slot_width + spacing)
            
            # Dark recess
            painter.fillRect(QRectF(x, start_y, slot_width, slot_height), dark_color)
            # Light highlight on the right lip
            painter.fillRect(QRectF(x + slot_width, start_y, 1, slot_height), light_color)
            
    else:
        slot_height = 3
        slot_width = rect.width()
        total_height = num_vents * slot_height + (num_vents - 1) * spacing
        offset_y = start_y + (rect.height() - total_height) / 2
        
        for i in range(num_vents):
            y = offset_y + i * (slot_height + spacing)
            
            # Dark recess
            painter.fillRect(QRectF(start_x, y, slot_width, slot_height), dark_color)
            # Light highlight on bottom lip
            painter.fillRect(QRectF(start_x, y + slot_height, slot_width, 1), light_color)
            
    painter.restore()
