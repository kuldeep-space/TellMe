"""
SidebarNavItem — A dedicated component for rendering Application Shell navigation.
Handles 6 states: Normal, Hover, Active, Focus, Disabled, Badge.
"""
from PySide6.QtGui import QPainter, QPaintEvent, QColor, QFont, QPixmap
from PySide6.QtCore import QRectF, Qt
from PySide6.QtWidgets import QAbstractButton
from PySide6.QtSvg import QSvgRenderer
from frontend.engine import StyleEngine
from frontend.core.navigation import NavigationItem

class SidebarNavItem(QAbstractButton):
    def __init__(self, engine: StyleEngine, item: NavigationItem, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.item = item
        
        self.setCheckable(True)
        self.setEnabled(item.enabled)
        self.setCursor(Qt.CursorShape.PointingHandCursor if item.enabled else Qt.CursorShape.ForbiddenCursor)
        
        # We need a fixed height for consistency in the sidebar
        self.setFixedHeight(34)
        
        # Load icon if present
        self._svg_renderer = None
        if item.icon:
            import os
            # Standard path for icons
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            icon_path = os.path.join(base_dir, "assets", "icons", item.icon)
            if os.path.exists(icon_path):
                self._svg_renderer = QSvgRenderer(icon_path)
        
        self.installEventFilter(self)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(self.rect())
        
        # State booleans
        is_active = self.isChecked()
        is_hovered = self.underMouse()
        is_disabled = not self.isEnabled()
        is_focused = self.hasFocus()
        
        # 1. Background (Hover / Active)
        if is_active or is_hovered:
            bg_alpha = 20 if is_active else 10 # 10% vs ~5% opacity
            fill_color = QColor(255, 255, 255, bg_alpha)
            painter.setBrush(fill_color)
            painter.setPen(Qt.PenStyle.NoPen)
            # Subtle rounded corners for the nav item
            painter.drawRoundedRect(rect, 6, 6)
            
        # 2. Active Indicator Pill
        if is_active:
            accent = self.engine.resolver.resolve_qcolor("colors.accent")
            painter.setBrush(accent)
            painter.setPen(Qt.PenStyle.NoPen)
            pill_height = rect.height() * 0.5
            pill_y = rect.y() + (rect.height() - pill_height) / 2
            painter.drawRoundedRect(QRectF(rect.x() + 2, pill_y, 3, pill_height), 1.5, 1.5)
            
        # 3. Focus Ring (Accessibility)
        if is_focused and not is_active:
            focus_color = self.engine.resolver.resolve_qcolor("colors.accent")
            focus_color.setAlpha(100)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(focus_color)
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 6, 6)

        # Determine colors based on state
        if is_disabled:
            text_color = self.engine.resolver.resolve_qcolor("colors.text_muted").darker(150)
            icon_color = text_color
        elif is_active:
            text_color = self.engine.resolver.resolve_qcolor("colors.text_primary")
            icon_color = text_color
        elif is_hovered:
            text_color = self.engine.resolver.resolve_qcolor("colors.text_primary").darker(110)
            icon_color = text_color
        else:
            text_color = self.engine.resolver.resolve_qcolor("colors.text_muted")
            icon_color = text_color

        # 4. Icon rendering with dynamic tinting
        left_padding = 12
        icon_size = 16
        icon_x = rect.x() + left_padding
        icon_y = rect.y() + (rect.height() - icon_size) / 2
        
        if self._svg_renderer:
            # Render SVG to pixmap, then tint it using SourceIn composition
            icon_pixmap = QPixmap(icon_size, icon_size)
            icon_pixmap.fill(Qt.GlobalColor.transparent)
            
            pix_painter = QPainter(icon_pixmap)
            pix_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self._svg_renderer.render(pix_painter, QRectF(0, 0, icon_size, icon_size))
            
            pix_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            pix_painter.fillRect(icon_pixmap.rect(), icon_color)
            pix_painter.end()
            
            painter.drawPixmap(int(icon_x), int(icon_y), icon_pixmap)
            
        # 5. Text rendering
        text_x = icon_x + icon_size + 12 if self._svg_renderer else left_padding
        text_rect = QRectF(text_x, rect.y(), rect.width() - text_x - 12, rect.height())
        
        painter.setPen(text_color)
        font = painter.font()
        font.setPixelSize(13)
        if is_active:
            font.setBold(True)
        painter.setFont(font)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.item.title)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.update()
