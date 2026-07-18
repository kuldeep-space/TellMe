from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QComboBox, QTextEdit, QFileDialog
from PySide6.QtCore import Qt
from backend.domain.interview_mode import InputField, FieldType
from frontend.core.app_context import AppContext

class FieldWidget(QWidget):
    """Base class for all dynamic form widgets. Handles label and description rendering."""
    def __init__(self, field: InputField, ctx: AppContext, parent=None):
        super().__init__(parent)
        self.field = field
        self.ctx = ctx
        self.setStyleSheet("background: transparent; border: none;")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)
        
        # Title Label
        t = self.ctx.ui.make_label(field.label, role="primary")
        t.setStyleSheet("background: transparent; border: none; font-weight: 600; font-size: 13px; color: #E8EAED; letter-spacing: 0.5px;")
        self._layout.addWidget(t)
        
        # Description
        if field.description:
            d = self.ctx.ui.make_label(field.description, role="muted")
            d.setStyleSheet("background: transparent; border: none; font-size: 12px; color: #9AA0A6;")
            d.setWordWrap(True)
            self._layout.addWidget(d)

    def get_value(self) -> Any:
        """Returns the current value of the widget."""
        raise NotImplementedError

# --- Implementations ---

class TextFieldWidget(FieldWidget):
    def __init__(self, field: InputField, ctx: AppContext, parent=None):
        super().__init__(field, ctx, parent)
        self.input = self.ctx.ui.make_input(placeholder=field.placeholder, prompt="")
        if hasattr(self.input, 'layout'):
            self.input.layout().setContentsMargins(0, 0, 0, 0)
            
        if hasattr(self.input, 'line_edit'):
            self.input.line_edit.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: #E8EAED;
                    font-size: 13px;
                }
                QLineEdit:hover {
                    background-color: rgba(255, 255, 255, 0.06);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
                QLineEdit:focus {
                    background-color: rgba(255, 255, 255, 0.08);
                    border: 1px solid #0F6ACD;
                }
            """)
        
        if field.default_value:
            self.input.set_text(str(field.default_value))
            
        self._layout.addWidget(self.input)

    def get_value(self) -> Any:
        return self.input.text()

class TextAreaFieldWidget(FieldWidget):
    def __init__(self, field: InputField, ctx: AppContext, parent=None):
        super().__init__(field, ctx, parent)
        self.textarea = QTextEdit()
        self.textarea.setPlaceholderText(field.placeholder)
        self.textarea.setMinimumHeight(120)
        self.textarea.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                color: #E8EAED;
                font-size: 13px;
            }
            QTextEdit:hover {
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QTextEdit:focus {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid #0F6ACD;
            }
        """)
        
        if field.default_value:
            self.textarea.setPlainText(str(field.default_value))
            
        self._layout.addWidget(self.textarea)

    def get_value(self) -> Any:
        return self.textarea.toPlainText()

class NonScrollingSpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()

class NumberFieldWidget(FieldWidget):
    def __init__(self, field: InputField, ctx: AppContext, parent=None):
        super().__init__(field, ctx, parent)
        self.spin = NonScrollingSpinBox()
        self.spin.setRange(0, 9999)
        self.spin.setFixedWidth(140)
        self.spin.setStyleSheet("""
            QSpinBox {
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: #E8EAED;
                font-size: 13px;
            }
            QSpinBox:hover {
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QSpinBox:focus {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid #0F6ACD;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px;
            }
        """)
        
        if field.default_value is not None:
            self.spin.setValue(int(field.default_value))
            
        container = QWidget()
        hl = QHBoxLayout(container)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.addWidget(self.spin)
        hl.addStretch()
        
        self._layout.addWidget(container)

    def get_value(self) -> Any:
        return self.spin.value()

class NonScrollingComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()

class DropdownFieldWidget(FieldWidget):
    def __init__(self, field: InputField, ctx: AppContext, parent=None):
        super().__init__(field, ctx, parent)
        self.combo = NonScrollingComboBox()
        self.combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: #E8EAED;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
                width: 32px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #9AA0A6;
                width: 0; height: 0;
                margin-right: 12px;
            }
            QComboBox:hover {
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QComboBox:focus {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid #0F6ACD;
            }
            QComboBox QAbstractItemView {
                background-color: #1A1C23;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: #E8EAED;
                selection-background-color: #0F6ACD;
                selection-color: white;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
            }
        """)
        
        if field.options:
            self.combo.addItems(field.options)
            
        if field.default_value and str(field.default_value) in field.options:
            self.combo.setCurrentText(str(field.default_value))
            
        self._layout.addWidget(self.combo)

    def get_value(self) -> Any:
        return self.combo.currentText()

class FileFieldWidget(FieldWidget):
    def __init__(self, field: InputField, ctx: AppContext, parent=None):
        super().__init__(field, ctx, parent)
        self.file_path = ""
        
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        
        # Display existing resume if applicable (Resume mode specifically, or general saved files later)
        # For this implementation, we check if the field ID is 'resume' and if we have one in profile.
        # But to keep it generic, we just check field.default_value as a path
        
        self.path_display = self.ctx.ui.make_input(placeholder=field.placeholder, prompt="")
        if hasattr(self.path_display, 'layout'):
            self.path_display.layout().setContentsMargins(0, 0, 0, 0)
            
        if hasattr(self.path_display, 'line_edit'):
            self.path_display.line_edit.setReadOnly(True)
            self.path_display.line_edit.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: #E8EAED;
                    font-size: 13px;
                }
            """)
            
        if field.default_value:
            self.file_path = str(field.default_value)
            self.path_display.set_text(f"✓ {self.file_path.split('/')[-1].split(chr(92))[-1]}")
            
        btn_text = "Replace" if field.default_value else "Browse"
        self.browse_btn = self.ctx.ui.make_button(btn_text)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 16px;
                color: #E8EAED;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.25);
            }
        """)
        self.browse_btn.clicked.connect(self._browse)
        
        self.clear_btn = self.ctx.ui.make_button("✕")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: #E8EAED;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 82, 82, 0.15);
                border: 1px solid rgba(255, 82, 82, 0.4);
                color: #FF5252;
            }
        """)
        self.clear_btn.setFixedWidth(40)
        self.clear_btn.clicked.connect(self._clear)
        self.clear_btn.setVisible(bool(self.file_path))
        
        row.addWidget(self.path_display, stretch=1)
        row.addWidget(self.clear_btn)
        row.addWidget(self.browse_btn)
        
        self._layout.addLayout(row)

    def _clear(self):
        self.file_path = ""
        self.path_display.set_text("")
        self.clear_btn.setVisible(False)
        self.browse_btn.setText("Browse")

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, f"Select {self.field.label}", "", "PDF Files (*.pdf);;All Files (*)")
        if path:
            self.file_path = path
            self.path_display.set_text(f"✓ {path.split('/')[-1].split(chr(92))[-1]}")
            self.clear_btn.setVisible(True)
            self.browse_btn.setText("Replace")

    def get_value(self) -> Any:
        return self.file_path

# --- Factory ---
class WidgetFactory:
    _registry = {
        FieldType.TEXT: TextFieldWidget,
        FieldType.TEXTAREA: TextAreaFieldWidget,
        FieldType.NUMBER: NumberFieldWidget,
        FieldType.DROPDOWN: DropdownFieldWidget,
        FieldType.FILE: FileFieldWidget
    }
    
    @classmethod
    def create(cls, field: InputField, ctx: AppContext, parent=None) -> FieldWidget:
        widget_class = cls._registry.get(field.type)
        if not widget_class:
            raise ValueError(f"No widget registered for field type: {field.type}")
        return widget_class(field, ctx, parent)
