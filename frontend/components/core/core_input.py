"""
CoreInput — shell-prompt prefixed single-line input.
TerminalTextArea — multi-line terminal text editor.
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QTextCursor

from frontend.components.base.base_input import BaseInput
from frontend.components.base.base_textarea import BaseTextarea
from frontend.engine import StyleEngine


class CoreInput(QWidget):
    """
    A single-line input prefixed by a shell prompt.

        user@tellme:~$ _

    Emits: text_submitted(str) on Enter key.
    """
    text_submitted = Signal(str)
    text_changed   = Signal(str)

    def __init__(self, prompt: str = "$ ", placeholder: str = "", engine: StyleEngine = None, parent=None):
        super().__init__(parent)
        self._prompt = prompt
        self._engine = engine

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._prompt_label = QLabel(prompt)
        prompt_color = "#33ff00"
        if engine:
            prompt_color = engine.resolver.resolve_color("colors.text_primary")
            
        self._prompt_label.setStyleSheet(
            f"color: {prompt_color};"
            f"background: transparent;"
            f"font-size: 12px; padding: 0;"
        )
        self._prompt_label.setFixedWidth(len(prompt) * 8 + 4)

        if engine:
            self._input = BaseInput(engine, placeholder)
        else:
            self._input = QLineEdit()
            self._input.setPlaceholderText(placeholder)
            
        self._input.setObjectName("terminalInput")
        self._input.returnPressed.connect(self._on_submit)
        self._input.textChanged.connect(self.text_changed)

        layout.addWidget(self._prompt_label)
        layout.addWidget(self._input, stretch=1)

    def _on_submit(self):
        self.text_submitted.emit(self._input.text())

    def text(self) -> str:
        return self._input.text()

    def set_text(self, value: str):
        self._input.setText(value)

    def clear(self):
        self._input.clear()

    def set_prompt(self, prompt: str):
        self._prompt = prompt
        self._prompt_label.setText(prompt)
        self._prompt_label.setFixedWidth(len(prompt) * 8 + 4)

    def set_read_only(self, ro: bool):
        self._input.setReadOnly(ro)

    def setPlaceholderText(self, text: str):
        self._input.setPlaceholderText(text)


class TerminalTextArea(BaseTextarea):
    """Multi-line terminal text editor."""

    def __init__(self, parent=None, read_only: bool = False, engine: StyleEngine = None):
        super().__init__(engine, parent)
        self.setObjectName("terminalTextEdit")
        self.setReadOnly(read_only)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

    def append_line(self, text: str, color: str = ""):
        """Append a line of text, scrolling to the bottom."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        if color:
            self.insertHtml(f'<span style="color:{color}; font-family: monospace">{text}<br></span>')
        else:
            self.insertPlainText(text + "\n")
        self.ensureCursorVisible()
