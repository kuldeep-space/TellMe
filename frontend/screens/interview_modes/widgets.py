from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QSize
from frontend.components.card.surface_card import SurfaceCard

class HeroSection(QWidget):
    def __init__(self, start_callback, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Welcome back!")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        
        subtitle = QLabel("Ready to nail your next interview?")
        subtitle.setStyleSheet("font-size: 16px; color: #A0A0A0;")
        
        start_btn = QPushButton("Start New Interview")
        start_btn.setObjectName("primaryButton")
        start_btn.clicked.connect(start_callback)
        start_btn.setFixedSize(200, 48)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(16)
        layout.addWidget(start_btn)
        
class QuickActionCard(SurfaceCard):
    def __init__(self, title_text, icon, callback, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._callback = callback
        
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 16px; font-weight: 500;")
        
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(24, 24))
        
        row = QHBoxLayout()
        row.addWidget(icon_label)
        row.addWidget(title)
        row.addStretch()
        
        self.addLayout(row)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._callback:
                self._callback()
        super().mousePressEvent(event)
