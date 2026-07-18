"""
BaseTextarea — Abstract base for multi-line text input/display.
"""
from PySide6.QtWidgets import QTextEdit
from frontend.engine import StyleEngine

class BaseTextarea(QTextEdit):
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(parent)
        self._engine = engine
        
    def append_line(self, text: str, color_hex: str = None):
        """Append text with an optional hex color."""
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        if color_hex:
            self.append(f'<span style="color: {color_hex};">{escaped}</span>')
        else:
            self.append(escaped)

    @property
    def engine(self) -> StyleEngine:
        return self._engine
