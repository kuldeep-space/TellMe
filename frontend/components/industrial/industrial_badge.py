"""
IndustrialBadge — Uses LedIndicator alongside text.
"""
from PySide6.QtWidgets import QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from frontend.components.base.base_badge import BaseBadge
from frontend.themes.base_theme import BadgeLevel
from frontend.engine import StyleEngine
from frontend.components.industrial.led_indicator import LedIndicator

class IndustrialBadge(BaseBadge):
    def __init__(self, engine: StyleEngine, text: str = "", level: BadgeLevel = BadgeLevel.INFO, parent=None):
        super().__init__(engine, text, level, parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)
        
        self._led = LedIndicator(engine, "led.info_color")
        self._label = QLabel(text)
        
        layout.addWidget(self._led)
        layout.addWidget(self._label)
        
        self.set_level(level)
        
    def set_level(self, level: BadgeLevel):
        super().set_level(level)
        if not hasattr(self, '_led'):
            return
            
        color_map = {
            BadgeLevel.OK: "led.online_color",
            BadgeLevel.ERR: "led.error_color",
            BadgeLevel.WARN: "led.warn_color",
            BadgeLevel.INFO: "led.info_color",
            BadgeLevel.BUSY: "led.warn_color",
            BadgeLevel.OFFLINE: "led.offline_color",
        }
        self._led._color_token = color_map.get(level, "led.info_color")
        self._led.update()
