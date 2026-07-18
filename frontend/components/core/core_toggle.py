"""
CoreToggle — boolean switch rendered as [ON] / [OFF] button.
"""
from frontend.components.base.base_toggle import BaseToggle
from frontend.engine import StyleEngine
from PySide6.QtCore import Qt, Signal

class CoreToggle(BaseToggle):
    """Clickable on/off toggle styled as [ ON ] / [OFF]."""

    toggled_state = Signal(bool)  # emits True when ON

    def __init__(self, initial: bool = False, engine: StyleEngine = None, parent=None):
        super().__init__(engine, "", parent)
        self.setObjectName("terminalToggle")
        self._state = initial
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedWidth(72)
        self.setMinimumHeight(26)
        self.clicked.connect(self._toggle)
        self._refresh()

    def _toggle(self):
        self._state = not self._state
        self._refresh()
        self.toggled_state.emit(self._state)

    def _refresh(self):
        primary = "#33ff00"
        inverse = "#0a0a0a"
        bg = "#0a0a0a"
        muted = "#456145"
        border = "#1f521f"
        
        if self._engine:
            primary = self._engine.resolver.resolve_color("colors.text_primary")
            inverse = self._engine.resolver.resolve_color("colors.text_inverse")
            bg = self._engine.resolver.resolve_color("colors.background")
            muted = self._engine.resolver.resolve_color("colors.text_muted")
            border = self._engine.resolver.resolve_color("colors.border")

        # Disable native checkbox indicator
        base_style = "QCheckBox::indicator { width: 0px; height: 0px; } "
            
        if self._state:
            self.setText("[ ON ]")
            self.setStyleSheet(base_style + 
                f"background-color: {primary};"
                f"color: {inverse};"
                f"border: 1px solid {primary};"
                f"padding: 3px 6px; font-size: 12px;"
            )
        else:
            self.setText("[OFF]")
            self.setStyleSheet(base_style + 
                f"background-color: {bg};"
                f"color: {muted};"
                f"border: 1px solid {border};"
                f"padding: 3px 6px; font-size: 12px;"
            )

    def is_on(self) -> bool:
        return self._state

    def set_state(self, value: bool):
        if self._state != value:
            self._state = value
            self._refresh()
