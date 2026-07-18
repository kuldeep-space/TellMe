from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from frontend.components.card.surface_card import SurfaceCard

class FileDropZone(SurfaceCard):
    file_dropped = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        
        self.label = QLabel("Drag & Drop your Resume (PDF) here\nor click to browse")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: {TEXT_SECONDARY};")
        
        self.addWidget(self.label)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("background-color: {SURFACE_HOVER}; border: 1px dashed {PRIMARY};")
            
    def dragLeaveEvent(self, event):
        self.setStyleSheet("") # reset
        
    def dropEvent(self, event):
        self.setStyleSheet("")
        for url in event.mimeData().urls():
            if url.isLocalFile() and url.toLocalFile().lower().endswith('.pdf'):
                self.file_dropped.emit(url.toLocalFile())
                self.label.setText(f"Selected: {url.fileName()}")
                break

class SegmentedControl(QWidget):
    selection_changed = Signal(str)
    
    def __init__(self, options, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        self.setObjectName("segmentedControl")
        self.setStyleSheet("background-color: {BACKGROUND}; border-radius: 8px; border: 1px solid {BORDER};")
        
        self.buttons = {}
        for opt in options:
            btn = QPushButton(opt)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:checked {
                    background-color: {SURFACE};
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(lambda _, text=opt: self._select(text))
            layout.addWidget(btn)
            self.buttons[opt] = btn
            
        if options:
            self._select(options[0])
            
    def _select(self, option):
        for text, btn in self.buttons.items():
            btn.setChecked(text == option)
        self.selection_changed.emit(option)
