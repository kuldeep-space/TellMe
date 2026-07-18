"""
BasePanel — The fundamental container widget.
"""
from PySide6.QtWidgets import QFrame
from typing import Any
from frontend.engine import StyleEngine

class BasePanel(QFrame):
    """
    Base class for panels.
    Supports elevations (chassis, panel, floating, recessed).
    """
    def __init__(self, engine: StyleEngine, elevation: str = "panel", parent=None):
        super().__init__(parent)
        self._engine = engine
        self._elevation = elevation
        # Typically panels don't draw frame unless styled
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setProperty("elevation", elevation)
        
    @property
    def engine(self) -> StyleEngine:
        return self._engine
        
    def add_widget(self, widget, stretch: int = 0):
        self.body_layout.addWidget(widget, stretch)
        
    def add_layout(self, layout, stretch: int = 0):
        self.body_layout.addLayout(layout, stretch)
        
    def add_stretch(self, stretch: int = 1):
        self.body_layout.addStretch(stretch)
        
    def clear(self):
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
