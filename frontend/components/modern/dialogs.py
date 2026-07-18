from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QGraphicsDropShadowEffect, QListWidget, QListWidgetItem,
    QGraphicsBlurEffect
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor
from typing import Optional

class ModernDialogBase(QDialog):
    """
    A base frameless dialog with rounded corners and a drop shadow.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.bg_widget = QWidget()
        self.bg_widget.setObjectName("dialogBg")
        self.bg_widget.setStyleSheet("""
            QWidget#dialogBg {
                background-color: #1A1A1A;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 10)
        self.bg_widget.setGraphicsEffect(shadow)
        
        self.main_layout.addWidget(self.bg_widget)
        
        self.content_layout = QVBoxLayout(self.bg_widget)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(16)
        self._parent_original_effect = None
        self._target_window: Optional[QWidget] = None
        self._dim_overlay: Optional[QWidget] = None

    def showEvent(self, event):
        super().showEvent(event)
        parent = self.parentWidget()
        self._target_window = parent.window() if parent else None
        
        if self._target_window:
            self._dim_overlay = QWidget(self._target_window)
            self._dim_overlay.setObjectName("dimOverlay")
            self._dim_overlay.setStyleSheet("QWidget#dimOverlay { background-color: rgba(0, 0, 0, 180); }")
            self._dim_overlay.setGeometry(self._target_window.rect())
            self._dim_overlay.show()
            # Hook resize event to keep overlay full size
            self._target_window.installEventFilter(self)

    def hideEvent(self, event):
        super().hideEvent(event)
        if hasattr(self, '_dim_overlay') and self._dim_overlay:
            if self._target_window:
                self._target_window.removeEventFilter(self)
            self._dim_overlay.hide()
            self._dim_overlay.deleteLater()
            self._dim_overlay = None

    def eventFilter(self, obj, event):
        if self._target_window and obj == self._target_window and event.type() == event.Type.Resize:
            if hasattr(self, '_dim_overlay') and self._dim_overlay:
                self._dim_overlay.setGeometry(self._target_window.rect())
        return super().eventFilter(obj, event)

    def _create_button(self, text, role="primary"):
        btn = QPushButton(text)
        if role == "primary":
            btn.setStyleSheet("""
                QPushButton {
                    background: #0F6ACD;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover { background: #137DEB; }
                QPushButton:pressed { background: #0B4F9A; }
            """)
        elif role == "danger":
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(239, 68, 68, 0.1);
                    color: #ef4444;
                    border: 1px solid rgba(239, 68, 68, 0.2);
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover { background: rgba(239, 68, 68, 0.2); }
                QPushButton:pressed { background: rgba(239, 68, 68, 0.3); }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #E8EAED;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 6px;
                    padding: 8px 16px;
                }
                QPushButton:hover { background: rgba(255, 255, 255, 0.1); }
                QPushButton:pressed { background: rgba(255, 255, 255, 0.15); }
            """)
        return btn


class ModernMessageDialog(ModernDialogBase):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(350)
        
        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        self.content_layout.addWidget(title_lbl)
        
        # Message
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color: #A0A0A0; font-size: 13px;")
        self.content_layout.addWidget(msg_lbl)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self.content_layout.addLayout(self.button_layout)
        
        self.clicked_button = None

    def add_button(self, text, role="primary"):
        btn = self._create_button(text, role)
        btn.clicked.connect(lambda: self._on_btn_clicked(text))
        self.button_layout.addWidget(btn)
        return btn
        
    def _on_btn_clicked(self, text):
        self.clicked_button = text
        self.accept()


class ModernListDialog(ModernDialogBase):
    def __init__(self, title, items, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(350)
        
        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        self.content_layout.addWidget(title_lbl)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: white;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QListWidget::item:selected {
                background: rgba(15, 106, 205, 0.3);
                border-left: 3px solid #0F6ACD;
            }
            QListWidget::item:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        for item in items:
            self.list_widget.addItem(item)
        self.content_layout.addWidget(self.list_widget)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        
        cancel_btn = self._create_button("Cancel", role="secondary")
        cancel_btn.clicked.connect(self.reject)
        
        select_btn = self._create_button("Select", role="primary")
        select_btn.clicked.connect(self.accept)
        
        self.button_layout.addWidget(cancel_btn)
        self.button_layout.addWidget(select_btn)
        self.content_layout.addLayout(self.button_layout)
        
        self.selected_item = None
        self.list_widget.itemDoubleClicked.connect(self.accept)

    def accept(self):
        curr = self.list_widget.currentItem()
        if curr:
            self.selected_item = curr.text()
            super().accept()
