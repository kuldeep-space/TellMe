from PySide6.QtWidgets import QWidget, QVBoxLayout
from frontend.engine import StyleEngine

class ModernPanel(QWidget):
    """
    Modern minimalist container. Flat, slightly rounded, clean padding.
    """
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setObjectName("ModernPanel")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(16)
        

    @property
    def body_layout(self):
        return self.main_layout

    def add_widget(self, widget: QWidget, stretch: int = 0):
        self.main_layout.addWidget(widget, stretch)

    def add_stretch(self, stretch: int = 1):
        self.main_layout.addStretch(stretch)

    def add_layout(self, layout):
        self.main_layout.addLayout(layout)
