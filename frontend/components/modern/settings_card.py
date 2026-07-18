from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

class SettingsCard(QFrame):
    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsCard")
        # Premium dark aesthetic
        self.setStyleSheet("""
            QFrame#SettingsCard {
                background-color: #15171A;
                border: 1px solid #272A30;
                border-radius: 10px;
            }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)
        
        # Header (Title + Description)
        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent; border: none;")
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #E2E8F0; font-size: 15px; font-weight: 600; background: transparent; border: none;")
        header_layout.addWidget(self.title_label)
        
        if description:
            self.desc_label = QLabel(description)
            self.desc_label.setStyleSheet("color: #94A3B8; font-size: 13px; background: transparent; border: none;")
            self.desc_label.setWordWrap(True)
            header_layout.addWidget(self.desc_label)
            
        self.main_layout.addWidget(header_widget)
        
        # Content Container (for fields)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(16)
        self.main_layout.addLayout(self.content_layout)
        
    def addWidget(self, widget: QWidget):
        self.content_layout.addWidget(widget)
        
    def addLayout(self, layout):
        self.content_layout.addLayout(layout)
