"""
CoreProgress — ASCII block progress bar widget.

Renders:  [########------]  42%
"""
from PySide6.QtWidgets import QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from frontend.components.base.base_progress import BaseProgress
from frontend.engine import StyleEngine

class CoreProgress(BaseProgress):
    """
    Renders a terminal-style ASCII progress bar.
    Width is number of characters in the bar (default 20).
    """

    def __init__(self, width: int = 20, engine: StyleEngine = None, parent=None, *, show_percent: bool = True):
        super().__init__(engine, parent)
        self.setObjectName("terminalProgress")
        self._bar_width  = width
        self._show_pct   = show_percent
        
        # Hide the native QProgressBar appearance
        self.setStyleSheet("QProgressBar { background: transparent; border: none; } QProgressBar::chunk { background: transparent; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._bar_label = QLabel(self._render(0))
        color = "#33ff00"
        if engine:
            color = engine.resolver.resolve_color("colors.text_primary")
            
        self._bar_label.setStyleSheet(
            f"color: {color}; font-size: 12px; background: transparent;"
        )
        layout.addWidget(self._bar_label)
        layout.addStretch()

    def _render(self, value: int) -> str:
        filled = int(self._bar_width * value / 100)
        empty  = self._bar_width - filled
        bar    = "#" * filled + "-" * empty
        if self._show_pct:
            return f"[{bar}] {value:3d}%"
        return f"[{bar}]"

    def set_value(self, value: int):
        """Set progress 0–100."""
        val = max(0, min(100, value))
        self.setValue(val)
        self._bar_label.setText(self._render(val))

    # value() is inherited from QProgressBar, returns self.value()
