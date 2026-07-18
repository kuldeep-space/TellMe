from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PySide6.QtCore import Qt
from frontend.engine import StyleEngine

class ModernInput(QWidget):
    """
    Modern input field. Clean background fill, soft rounded corners, no harsh borders.
    """
    def __init__(self, engine: StyleEngine, placeholder: str = "", prompt: str = "", parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setObjectName("ModernInputContainer")
        self.setMinimumHeight(40)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        if prompt:
            self.prompt_lbl = QLabel(prompt)
            self.prompt_lbl.setObjectName("ModernInputPrompt")
            layout.addWidget(self.prompt_lbl)
            
        self.line_edit = QLineEdit()
        self.line_edit.setObjectName("ModernInputBox")
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setFrame(False)
        layout.addWidget(self.line_edit, stretch=1)
        

    @property
    def textChanged(self):
        return self.line_edit.textChanged

    def text(self) -> str:
        return self.line_edit.text()

    def set_text(self, text: str):
        self.line_edit.setText(text)

    def setFocus(self, reason=Qt.FocusReason.OtherFocusReason):
        self.line_edit.setFocus(reason)
