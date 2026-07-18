"""
CoreButton — [ LABEL ] style buttons with hover-invert behaviour.
"""
from PySide6.QtCore import Qt
from frontend.components.base.base_button import BaseButton
from frontend.themes.base_theme import ButtonVariant
from frontend.engine import StyleEngine

class CoreButton(BaseButton):
    """Primary terminal button — renders as  [ LABEL ]  with invert-on-hover."""

    def __init__(self, label: str, engine: StyleEngine = None, variant: ButtonVariant = ButtonVariant.PRIMARY, parent=None):
        super().__init__(engine, f"[ {label.upper()} ]", variant, parent)
        self.setObjectName("terminalButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Backward compatibility for styling without engine setup yet
        if variant == ButtonVariant.DANGER:
            self.setObjectName("terminalButtonDanger")
        elif variant == ButtonVariant.WARNING:
            self.setObjectName("terminalButtonWarning")
            
        if engine:
            min_height = engine.resolver.resolve_int("layout.button_min_height")
            self.setMinimumHeight(min_height)
        else:
            self.setMinimumHeight(28)

    def set_label(self, label: str):
        self.setText(f"[ {label.upper()} ]")


class CoreButtonDanger(CoreButton):
    """Danger-coloured terminal button."""

    def __init__(self, label: str, engine: StyleEngine = None, parent=None):
        super().__init__(label, engine, ButtonVariant.DANGER, parent)

    def set_label(self, label: str):
        self.setText(f"[ {label.upper()} ]")


class CoreButtonWarning(CoreButton):
    """Warning-coloured terminal button."""

    def __init__(self, label: str, engine: StyleEngine = None, parent=None):
        super().__init__(label, engine, ButtonVariant.WARNING, parent)

    def set_label(self, label: str):
        self.setText(f"[ {label.upper()} ]")

