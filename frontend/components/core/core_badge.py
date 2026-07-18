"""
CoreBadge — inline status indicator rendered as text.

Examples:
    [  OK  ]   green
    [ ERR  ]   red
    [ WARN ]   amber
    [ INFO ]   cyan
    [ BUSY ]   dim
"""
from frontend.components.base.base_badge import BaseBadge
from frontend.themes.base_theme import BadgeLevel
from frontend.engine import StyleEngine

class CoreBadge(BaseBadge):
    """Inline status badge."""

    def __init__(self, level: BadgeLevel = BadgeLevel.OK, engine: StyleEngine = None, parent=None):
        super().__init__(engine, "", level, parent)
        self.setObjectName("terminalBadge")
        self.set_level(level)

    def set_level(self, level: BadgeLevel):
        super().set_level(level)
        text  = f"[ {level.value:^6} ]"
        self.setText(text)
        
        # Backward compatibility without engine
        if self._engine is None:
            # simple fallback
            colors = {
                BadgeLevel.OK: "#33ff00",
                BadgeLevel.ERR: "#ff3333",
                BadgeLevel.WARN: "#ffb000",
                BadgeLevel.INFO: "#33ffcc",
                BadgeLevel.BUSY: "#456145",
                BadgeLevel.OFFLINE: "#2a3d2a",
            }
            color = colors.get(level, "#456145")
            self.setStyleSheet(
                f"color: {color}; background: transparent; font-size: 11px;"
            )
