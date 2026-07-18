"""
IndustrialButton — Neumorphic mechanical button.
"""
from PySide6.QtGui import QPainter, QPaintEvent, QColor, QFont
from PySide6.QtCore import QRectF, Qt, Property, QPropertyAnimation
from frontend.components.base.base_button import BaseButton
from frontend.engine import StyleEngine
from frontend.themes.base_theme import ButtonVariant
from frontend.components.industrial.painters.neumorphic import draw_neumorphic_panel, draw_inset_shadow

class IndustrialButton(BaseButton):
    def __init__(self, engine: StyleEngine, text: str = "", variant: ButtonVariant = ButtonVariant.PRIMARY, parent=None, text_align=Qt.AlignmentFlag.AlignCenter, icon_path: str = None, left_padding: int = 16):
        super().__init__(engine, text, variant, parent)
        self._text_align = text_align
        self._left_padding = left_padding
        self._icon_path = icon_path
        if self._icon_path:
            from PySide6.QtSvg import QSvgRenderer
            self._svg_renderer = QSvgRenderer(self._icon_path)
        else:
            self._svg_renderer = None
        self.setMinimumHeight(engine.resolver.resolve_int("layout.button_min_height"))
        
        # Animations
        self._hover_enter, self._hover_leave = engine.anim.register_hover_lift(self, lift_px=1)
        self._press, self._release = engine.anim.register_press_depress(self, depress_px=2)
        
        # Custom properties for animation
        self._lift = 0.0
        
        self.installEventFilter(self)

    @Property(float)
    def lift(self) -> float:
        return self._lift
        
    @lift.setter
    def lift(self, value: float):
        self._lift = value
        self.update()

    def enterEvent(self, event):
        super().enterEvent(event)
        # self._hover_enter.start()  # Assuming we animate lift property
        
    def leaveEvent(self, event):
        super().leaveEvent(event)
        # self._hover_leave.start()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        rect = QRectF(self.rect())
        
        radius = self.engine.resolver.resolve_int("radius.md")
        bg_color = self.engine.resolver.resolve_qcolor("colors.surface")
        
        # For Primary/Danger/Warning, mix in the accent
        if self.variant == ButtonVariant.PRIMARY:
            bg_color = self.engine.resolver.resolve_qcolor("colors.accent")
        elif self.variant == ButtonVariant.DANGER:
            bg_color = self.engine.resolver.resolve_qcolor("status.danger")
            
        dark_shadow = QColor(0, 0, 0, 120)
        light_shadow = QColor(255, 255, 255, 30)
        
        if self.variant == ButtonVariant.GHOST:
            # Modern, sleek web-like navigation style (e.g. Linear / Cursor)
            is_active = self.isChecked() or self.isDown()
            is_hovered = self.underMouse()
            
            if is_active or is_hovered:
                # Sleek, borderless background
                bg_alpha = 25 if is_active else 12
                fill_color = QColor(255, 255, 255, bg_alpha)
                painter.setBrush(fill_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(rect, 6, 6)
                
            # Elegant pill-shaped left indicator if active
            if self.isChecked():
                accent = self.engine.resolver.resolve_qcolor("colors.accent")
                painter.setBrush(accent)
                painter.setPen(Qt.PenStyle.NoPen)
                # Pill vertically centered
                pill_height = rect.height() * 0.4
                pill_y = rect.y() + (rect.height() - pill_height) / 2
                painter.drawRoundedRect(QRectF(rect.x() + 2, pill_y, 3, pill_height), 1.5, 1.5)
        else:
            if self.isDown():
                # Inset shadow when pressed for non-ghost
                painter.setBrush(bg_color.darker(110))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(rect, radius, radius)
                draw_inset_shadow(painter, rect, radius, dark_shadow, light_shadow)
            elif self.underMouse() or self.isChecked():
                # Hover state for neumorphic
                draw_neumorphic_panel(painter, rect, radius, bg_color.lighter(105), dark_shadow, light_shadow)
            else:
                # Normal neumorphic raised
                draw_neumorphic_panel(painter, rect, radius, bg_color, dark_shadow, light_shadow)

        # Determine text and icon color
        icon_opacity = 1.0
        if self.variant == ButtonVariant.GHOST:
            if self.isChecked() or self.underMouse() or self.isDown():
                text_color = self.engine.resolver.resolve_qcolor("colors.text_primary")
            else:
                text_color = self.engine.resolver.resolve_qcolor("colors.text_muted")
                icon_opacity = 0.5
        else:
            text_color = self.engine.resolver.resolve_qcolor("colors.text_primary")
            if self.isDown():
                text_color = text_color.darker(120)
                
        painter.setPen(text_color)
        
        content_rect = QRectF(rect.x() + self._left_padding, rect.y(), rect.width() - self._left_padding - 16, rect.height())
        
        # If there's an icon, draw it and offset the text
        if self._svg_renderer:
            icon_size = 18
            # Calculate Y to vertically center the icon
            icon_y = content_rect.y() + (content_rect.height() - icon_size) / 2
            
            # Since QSvgRenderer doesn't easily tint SVG dynamically without parsing, 
            # we will just draw it as is, but we can set opacity if disabled
            painter.save()
            painter.setOpacity(icon_opacity)
            # Try to colorize if possible using composition mode, but plain drawing is safer.
            self._svg_renderer.render(painter, QRectF(content_rect.x(), icon_y, icon_size, icon_size))
            painter.restore()
            
            # Offset text by icon_size + padding
            text_rect = QRectF(content_rect.x() + icon_size + 12, content_rect.y(), content_rect.width() - icon_size - 12, content_rect.height())
        else:
            text_rect = content_rect
            
        # Draw text
        painter.drawText(text_rect, self._text_align | Qt.AlignmentFlag.AlignVCenter, self.text())
