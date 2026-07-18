from PySide6.QtWidgets import QFrame, QVBoxLayout
from PySide6.QtCore import Qt

class SurfaceCard(QFrame):
    """
    A generic card with surface background, rounded corners and border.
    Uses objectName='surfaceCard' for styling in QSS.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("surfaceCard")
        
        self.card_layout = QVBoxLayout(self)
        self.card_layout.setContentsMargins(24, 24, 24, 24)
        self.card_layout.setSpacing(16)
        
    def addWidget(self, widget):
        self.card_layout.addWidget(widget)
        
    def addLayout(self, layout):
        self.card_layout.addLayout(layout)
