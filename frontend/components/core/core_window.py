"""
CoreWindow — a bordered pane with an ASCII title bar.

Usage:
    win = CoreWindow("SYSTEM STATUS")
    win.body_layout.addWidget(some_widget)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt

from frontend.components.base.base_panel import BasePanel
from frontend.engine import StyleEngine

class CoreWindow(BasePanel):
    """
    Renders a pane styled like a terminal window:

        +-- TITLE ------------------------------------------+
        |  content                                          |
        +---------------------------------------------------+
    """

    def __init__(self, title: str = "", engine: StyleEngine = None, parent=None, *, accent=False):
        super().__init__(engine, "panel", parent)
        self.setObjectName("terminalWindow")
        self._accent = accent

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Title bar
        self._title_bar = QLabel(f" {title.upper()} " if title else "")
        self._title_bar.setObjectName("terminalWindowTitle")
        self._title_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        if engine is None:
            if accent:
                self._title_bar.setStyleSheet(
                    f"background-color: #1f9900;"
                    f"color: #0a0a0a;"
                    f"font-size: 11px; padding: 2px 8px;"
                )
        else:
            # Let QSSHydrator style it via the theme's QSS file
            if accent:
                self._title_bar.setProperty("accent", True)
                
        outer.addWidget(self._title_bar)

        # Body widget
        self._body = QWidget()
        self._body.setObjectName("terminalWindowBody")
        
        if engine is None:
            self._body.setStyleSheet(
                f"QWidget#terminalWindowBody {{"
                f"  background-color: #101010;"
                f"  border-left: 1px solid #1f521f;"
                f"  border-right: 1px solid #1f521f;"
                f"  border-bottom: 1px solid #1f521f;"
                f"}}"
            )
        self.body_layout = QVBoxLayout(self._body)
        self.body_layout.setContentsMargins(12, 10, 12, 10)
        self.body_layout.setSpacing(6)
        outer.addWidget(self._body, stretch=1)

    def set_title(self, title: str):
        self._title_bar.setText(f" {title.upper()} ")

    def add_widget(self, widget):
        self.body_layout.addWidget(widget)

    def add_layout(self, layout):
        self.body_layout.addLayout(layout)

    def add_stretch(self, n: int = 1):
        self.body_layout.addStretch(n)
