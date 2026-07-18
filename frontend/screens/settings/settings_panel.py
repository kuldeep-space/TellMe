from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QFrame
from PySide6.QtCore import Qt, Signal
from frontend.core.app_context import AppContext
from .profile_page import ProfilePage
from .model_page import ModelSettingsPage
from frontend.components.modern.dialogs import ModernMessageDialog

class SettingsPanel(QWidget):
    """
    The main container for the Settings workspace.
    Manages switching between Profile and Model Settings, and handles unsaved changes.
    """
    
    close_requested = Signal()
    
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self._unsaved_changes = False
        
        self._build_ui()
        
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # Content stack (Top part, stretches)
        self.stack = QStackedWidget()
        
        from PySide6.QtWidgets import QScrollArea
        
        # Profile ScrollArea
        self.profile_scroll = QScrollArea()
        self.profile_scroll.setWidgetResizable(True)
        self.profile_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.profile_page = ProfilePage(self.ctx)
        self.profile_page.modified.connect(self._on_modified)
        self.profile_scroll.setWidget(self.profile_page)
        
        # Model Page — no outer scroll; ModelSettingsPage manages its own internal scroll areas
        self.model_page = ModelSettingsPage(self.ctx)
        self.model_page.modified.connect(self._on_modified)

        self.stack.addWidget(self.profile_scroll)
        self.stack.addWidget(self.model_page)
        
        root.addWidget(self.stack, stretch=1)
        
    def show_page(self, page_name: str):
        if page_name == "profile":
            self.stack.setCurrentIndex(0)
        elif page_name == "model_settings":
            self.stack.setCurrentIndex(1)
            
    def _on_modified(self):
        # Auto-save immediately instead of showing a banner
        self._save_changes()
        
    def _save_changes(self) -> bool:
        if self.profile_page.save() is False:
            return False
        self.model_page.save()
        return True
        
    def attempt_close(self) -> bool:
        return True
