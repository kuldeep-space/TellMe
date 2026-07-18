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
        
        # Model ScrollArea
        self.model_scroll = QScrollArea()
        self.model_scroll.setWidgetResizable(True)
        self.model_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.model_page = ModelSettingsPage(self.ctx)
        self.model_page.modified.connect(self._on_modified)
        self.model_scroll.setWidget(self.model_page)
        
        self.stack.addWidget(self.profile_scroll)
        self.stack.addWidget(self.model_scroll)
        
        root.addWidget(self.stack, stretch=1)

        # Save action bar (hidden by default)
        self.save_banner = QFrame()
        self.save_banner.setObjectName("SaveBanner")
        self.save_banner.setStyleSheet("""
            QFrame#SaveBanner {
                background: #1A1C20;
                border-top: 1px solid #272A30;
            }
        """)
        self.save_banner.hide()
        
        banner_layout = QHBoxLayout(self.save_banner)
        banner_layout.setContentsMargins(32, 16, 32, 16)
        
        warning_lbl = QLabel("Unsaved changes")
        warning_lbl.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 500;")
        banner_layout.addWidget(warning_lbl)
        
        banner_layout.addStretch()
        
        from frontend.themes.base_theme import ButtonVariant
        
        btn_discard = self.ctx.ui.make_button("Discard", variant=ButtonVariant.SECONDARY)
        btn_discard.clicked.connect(self._discard_changes)
        
        btn_save = self.ctx.ui.make_button("Save Changes", variant=ButtonVariant.PRIMARY)
        btn_save.clicked.connect(self._save_changes)
        
        banner_layout.addWidget(btn_discard)
        banner_layout.addWidget(btn_save)
        
        root.addWidget(self.save_banner)
        
    def show_page(self, page_name: str):
        if page_name == "profile":
            self.stack.setCurrentIndex(0)
        elif page_name == "model_settings":
            self.stack.setCurrentIndex(1)
            
    def _on_modified(self):
        self._unsaved_changes = True
        self.save_banner.show()
        
    def _discard_changes(self):
        # Reload current settings
        self.profile_page.reload()
        self.model_page.reload()
        self._unsaved_changes = False
        self.save_banner.hide()
        
    def _save_changes(self) -> bool:
        # Save current settings
        # if save() explicitly returns False (validation failed), abort
        if self.profile_page.save() is False:
            return False
            
        self.model_page.save()
        
        self._unsaved_changes = False
        self.save_banner.hide()
        return True
        
    def attempt_close(self) -> bool:
        """
        Returns True if safe to close.
        If there are unsaved changes, prompts the user.
        """
        if not self._unsaved_changes:
            return True
            
        dialog = ModernMessageDialog(
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save them before closing?",
            self
        )
        dialog.add_button("Save & Close", role="primary")
        dialog.add_button("Discard", role="danger")
        dialog.add_button("Cancel", role="secondary")
        
        dialog.exec()
        
        if dialog.clicked_button == "Save & Close":
            return self._save_changes()
        elif dialog.clicked_button == "Discard":
            self._discard_changes()
            return True
            
        return False
