import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from PySide6.QtCore import Qt, Signal
from frontend.core.app_context import AppContext

class ProfilePage(QWidget):
    """
    Minimal Profile Configuration.
    Manages user name and strictly uses internal managed resume storage.
    """
    
    modified = Signal()
    
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self._new_name: str = ""
        self._new_resume_path: str = ""
        self._resume_deleted = False
        
        self._build_ui()
        self.reload()
        
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)
        root.setSpacing(32)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Header
        title = QLabel("Profile")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #E2E8F0;")
        root.addWidget(title)
        
        from frontend.components.modern.settings_card import SettingsCard
        
        # Card 1: Personal Information
        self.personal_card = SettingsCard(
            title="Personal Information",
            description="This name will be used by the AI during your interview."
        )
        self.name_input = self.ctx.ui.make_input(placeholder="Enter your name")
        self.name_input.textChanged.connect(self._on_name_changed)
        self.personal_card.addWidget(self.name_input)
        
        self.name_error = QLabel()
        self.name_error.setStyleSheet("color: #FF5555; font-size: 12px; margin-top: 4px;")
        self.name_error.hide()
        self.personal_card.addWidget(self.name_error)
        
        root.addWidget(self.personal_card)
        
        # Card 2: Resume
        self.resume_card = SettingsCard(
            title="Resume",
            description="Manage the resume you use for context during interviews."
        )
        
        self.resume_status = QLabel()
        self.resume_status.setStyleSheet("color: #E2E8F0; font-size: 14px; margin-bottom: 8px;")
        self.resume_card.addWidget(self.resume_status)
        
        from frontend.themes.base_theme import ButtonVariant
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(12)
        
        self.btn_replace = self.ctx.ui.make_button("Upload Resume", variant=ButtonVariant.SECONDARY)
        self.btn_replace.clicked.connect(self._on_replace_resume)
        
        self.btn_delete = self.ctx.ui.make_button("Delete Resume", variant=ButtonVariant.DANGER)
        self.btn_delete.clicked.connect(self._on_delete_resume)
        
        btn_layout.addWidget(self.btn_replace)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        
        self.resume_card.addLayout(btn_layout)
        root.addWidget(self.resume_card)
        
        root.addStretch()
        
    def reload(self):
        profile = self.ctx.profile_service.current_profile
        self.name_input.line_edit.blockSignals(True)
        self.name_input.set_text(profile.name)
        self.name_input.line_edit.blockSignals(False)
        
        self._new_name = profile.name
        self._new_resume_path = profile.resume_path
        self._resume_deleted = False
        
        self._update_resume_ui()
        
    def _update_resume_ui(self):
        if self._resume_deleted or not self._new_resume_path:
            self.resume_status.setText("No Resume Uploaded.\nUpload a resume to enable Resume Interview mode.")
            self.resume_status.setStyleSheet("color: #94A3B8; font-size: 14px; margin-bottom: 8px;")
            self.btn_replace.setText("Upload Resume")
            self.btn_delete.hide()
        else:
            filename = os.path.basename(self._new_resume_path)
            self.resume_status.setText(f"✓ Current Resume: {filename}")
            self.resume_status.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 500; margin-bottom: 8px;")
            self.btn_replace.setText("Replace Resume")
            self.btn_delete.show()
            
    def _on_name_changed(self, text):
        self._new_name = text
        
        import re
        alpha_count = len(re.findall(r'[a-zA-Z]', text))
        
        if alpha_count < 3 and text.strip() != "":
            self.name_error.setText("Name must contain at least 3 alphabet characters.")
            self.name_error.show()
            self._name_valid = False
        else:
            self.name_error.hide()
            self._name_valid = True
            
        self.modified.emit()
        
    def _on_replace_resume(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Resume", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if path:
            self._new_resume_path = path
            self._resume_deleted = False
            self._update_resume_ui()
            self.modified.emit()
            
    def _on_delete_resume(self):
        self._resume_deleted = True
        self._new_resume_path = ""
        self._update_resume_ui()
        self.modified.emit()
        
    def save(self) -> bool:
        final_name = self._new_name.strip() if self._new_name else ""
        
        # If there's an active error, don't allow saving
        if not getattr(self, '_name_valid', True):
            return False
            
        # Re-validate if they somehow bypassed UI
        import re
        alpha_count = len(re.findall(r'[a-zA-Z]', final_name))
        
        profile = self.ctx.profile_service.current_profile
        
        # We only require 3 chars if they actually typed something new,
        # OR if they have no name and need to set one.
        # But if they cleared it, we either revert to old name or block it.
        if not final_name:
            if profile.name:
                final_name = profile.name
            else:
                self.name_error.setText("Name is required.")
                self.name_error.show()
                return False
        elif alpha_count < 3:
            self.name_error.setText("Name must contain at least 3 alphabet characters.")
            self.name_error.show()
            return False
            
        if final_name != profile.name or self._new_resume_path != profile.resume_path or self._resume_deleted:
            self.ctx.profile_service.update_profile(
                name=final_name,
                resume_path="" if self._resume_deleted else self._new_resume_path
            )
            self.reload()
            
        return True
