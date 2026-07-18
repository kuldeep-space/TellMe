"""
Onboarding Screen.
Displayed on first launch to collect user details.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QSpacerItem, QSizePolicy, QLabel
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QKeyEvent, QPixmap
from frontend.core.base_screen import BaseScreen
from frontend.core.app_context import AppContext
from frontend.themes.base_theme import ButtonVariant
from .viewmodel import OnboardingViewModel

class OnboardingScreen(BaseScreen):
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(ctx, parent)
        self.vm = OnboardingViewModel(ctx, self)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(40, 40, 40, 40)
        
        # Center everything vertically
        main.addStretch(1)
        
        # ── Branding ──────────────────────────────────────────────
        # Logo
        logo_lbl = QLabel()
        logo_pixmap = self.ctx.resource_manager.get_pixmap("Logo-without.png")
        if not logo_pixmap.isNull():
            logo_lbl.setPixmap(logo_pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(logo_lbl)
        
        main.addSpacing(16)
        
        brand_lbl = self.ctx.ui.make_label("TELLME", role="primary")
        font = brand_lbl.font()
        font.setPointSize(48)
        font.setBold(True)
        brand_lbl.setFont(font)
        brand_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(brand_lbl)
        
        main.addSpacing(8)
        
        sub_lbl = self.ctx.ui.make_label("Your AI Interview Coach", role="muted")
        font = sub_lbl.font()
        font.setPointSize(16)
        sub_lbl.setFont(font)
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(sub_lbl)
        
        main.addSpacing(64)
        
        # ── Form Container ──────────────────────────────────────────────
        form_container = QWidget()
        form_container.setFixedWidth(500)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(16)
        
        # Name
        self._name_input = self.ctx.ui.make_input(placeholder="Enter your name", prompt="Name")
        self._name_input.setFixedHeight(48)
        form_layout.addWidget(self._name_input)
        
        # Resume
        resume_row = QHBoxLayout()
        self._resume_input = self.ctx.ui.make_input(placeholder="Optional: Path to Resume PDF", prompt="Resume")
        self._resume_input.setFixedHeight(48)
        self._resume_btn = self.ctx.ui.make_button("BROWSE")
        self._resume_btn.setFixedHeight(48)
        self._resume_btn.clicked.connect(self._browse_resume)
        resume_row.addWidget(self._resume_input, stretch=1)
        resume_row.addWidget(self._resume_btn)
        form_layout.addLayout(resume_row)
        
        # Error Label
        self._error_lbl = self.ctx.ui.make_label("", role="muted")
        self._error_lbl.setStyleSheet(self._error_lbl.styleSheet() + " color: #ff5555;")
        self._error_lbl.hide()
        form_layout.addWidget(self._error_lbl)
        
        form_layout.addSpacing(20)
        
        # Buttons
        btn_row = QHBoxLayout()
        
        self._skip_btn = self.ctx.ui.make_button("SKIP RESUME", variant=ButtonVariant.GHOST)
        self._skip_btn.setFixedHeight(48)
        self._skip_btn.clicked.connect(lambda: self.vm.skip_resume_and_submit(self._name_input.text()))
        
        self._submit_btn = self.ctx.ui.make_button("CONTINUE", variant=ButtonVariant.PRIMARY)
        self._submit_btn.setFixedHeight(48)
        self._submit_btn.clicked.connect(lambda: self.vm.submit_profile(self._name_input.text(), self._resume_input.text()))
        
        btn_row.addStretch()
        btn_row.addWidget(self._skip_btn)
        btn_row.addWidget(self._submit_btn)
        
        form_layout.addLayout(btn_row)
        
        # Add form to main, centered horizontally
        form_h_center = QHBoxLayout()
        form_h_center.addStretch()
        form_h_center.addWidget(form_container)
        form_h_center.addStretch()
        main.addLayout(form_h_center)
        
        main.addStretch(1)

    def showEvent(self, event):
        """Automatically set focus to Name input when screen is shown."""
        super().showEvent(event)
        self._name_input.setFocus()

    def keyPressEvent(self, event: QKeyEvent):
        """Bind Enter key to submit."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.vm.submit_profile(self._name_input.text(), self._resume_input.text())
        else:
            super().keyPressEvent(event)

    def _connect_signals(self):
        self.vm.error_changed.connect(self._on_error)

    def _on_error(self, error: str):
        if error:
            self._error_lbl.setText(error)
            self._error_lbl.show()
        else:
            self._error_lbl.hide()

    def _browse_resume(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Resume", "", "PDF Files (*.pdf)")
        if path:
            self._resume_input.set_text(path)
