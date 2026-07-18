from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QToolButton
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QEnterEvent
from frontend.engine import StyleEngine

class SidebarSubItem(QWidget):
    """
    A child navigation item representing a Draft. 
    Shows a Close (X) button on hover.
    """
    clicked = Signal()
    close_requested = Signal()

    def __init__(self, engine: StyleEngine, title: str, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setFixedHeight(30)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 0, 8, 0) # Indented
        layout.setSpacing(4)
        
        # Determine colors
        text_color = engine.resolver.resolve_qcolor("colors.text_primary").name()
        hover_bg = engine.resolver.resolve_qcolor("colors.surface_hover").name()
        
        self.setStyleSheet(f"""
            SidebarSubItem {{
                background: transparent;
                border-radius: 4px;
            }}
            SidebarSubItem:hover {{
                background: {hover_bg};
            }}
        """)
        
        self.label = QLabel(title)
        self.label.setStyleSheet(f"color: {text_color}; font-size: 12px; font-weight: 500;")
        
        self.close_btn = QToolButton()
        self.close_btn.setText("✕")
        self.close_btn.setStyleSheet(f"""
            QToolButton {{
                background: transparent;
                border: none;
                color: {text_color};
                font-size: 14px;
                font-weight: bold;
                padding: 0;
                margin: 0;
            }}
            QToolButton:hover {{
                color: #ff4444;
            }}
        """)
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.close_requested.emit)
        
        # Hide close button initially
        self.close_btn.setVisible(False)
        
        layout.addWidget(self.label, 1)
        layout.addWidget(self.close_btn, 0)
        
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        
    def enterEvent(self, event: QEnterEvent):
        super().enterEvent(event)
        self.close_btn.setVisible(True)
        
    def leaveEvent(self, event: QEvent):
        super().leaveEvent(event)
        self.close_btn.setVisible(False)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
