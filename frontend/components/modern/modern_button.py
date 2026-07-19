from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor
from frontend.engine import StyleEngine
from frontend.themes.base_theme import ButtonVariant

class ModernButton(QPushButton):
    """
    Modern button with smooth hover states, rounded corners, and soft styling.
    """
    def __init__(self, engine: StyleEngine, text: str = "", variant: ButtonVariant = ButtonVariant.PRIMARY, parent=None):
        super().__init__(text, parent)
        self.engine = engine
        self.variant = variant
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(36)
        
        # Set dynamic object names for QSS targeting
        if variant == ButtonVariant.PRIMARY:
            self.setObjectName("ModernButtonPrimary")
        elif variant == ButtonVariant.SECONDARY:
            self.setObjectName("ModernButtonSecondary")
        elif variant == ButtonVariant.GHOST:
            self.setObjectName("ModernButtonGhost")
        elif variant == ButtonVariant.DANGER:
            self.setObjectName("ModernButtonDanger")
        elif variant == ButtonVariant.WARNING:
            self.setObjectName("ModernButtonWarning")

    def set_label(self, label: str):
        """Update button text — API compatibility with CoreButton."""
        self.setText(label)
