"""
Dynamic Interview Configuration Screen.
Purely schema-driven based on the selected interview mode.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QGridLayout, QLabel
)
from PySide6.QtCore import Qt

from frontend.core.base_screen import BaseScreen
from frontend.core.app_context import AppContext
from frontend.themes.base_theme import LabelRole
from backend.domain.interview_mode import InterviewRegistry
from .viewmodel import InterviewConfigViewModel
from .factory import WidgetFactory

PREMIUM_BTN_PRIMARY_QSS = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0F6ACD, stop:1 #0B4F9A);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px 24px;
        color: white;
        font-weight: bold;
        font-size: 14px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #137DEB, stop:1 #0E5EB3);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    QPushButton:pressed {
        background: #0B4F9A;
    }
"""

PREMIUM_BTN_SECONDARY_QSS = """
    QPushButton {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px 24px;
        color: #E8EAED;
        font-size: 13px;
        font-weight: 500;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.25);
    }
"""

class InterviewConfigScreen(BaseScreen):
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(ctx, parent)
        self.vm = InterviewConfigViewModel(ctx, self)
        self._current_mode_id = None
        
        # When activated, this screen builds itself dynamically based on the selected mode.
        self._build_ui()

    def showEvent(self, event):
        """Rebuild the UI when shown to match the active mode."""
        super().showEvent(event)
        
    def on_enter(self):
        self.vm.load_mode()
        
        draft_id = self.ctx.store.active_draft_id
        if not draft_id: return
        draft = self.ctx.draft_manager.get_draft(draft_id)
        if not draft: return
        
        # If the mode changed for this draft somehow, rebuild (shouldn't happen often)
        if self.vm.mode and self.vm.mode.id != self._current_mode_id:
            self._rebuild_dynamic_content()
            self._current_mode_id = self.vm.mode.id
        
        self.vm.hydrate_and_bind()
        
        # Restore scroll position
        self.scroll_area.verticalScrollBar().setValue(draft.scroll_position)
            
    def on_leave(self):
        draft_id = self.ctx.store.active_draft_id
        if draft_id:
            draft = self.ctx.draft_manager.get_draft(draft_id)
            if draft:
                draft.scroll_position = self.scroll_area.verticalScrollBar().value()

    def _build_ui(self):
        # ── Main Layout (Scroll Area) ────────────────────────────────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
            }
            QScrollBar:horizontal {
                border: none;
                background: transparent;
                height: 12px;
                margin: 0px 40px 0px 40px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(255, 255, 255, 0.2);
                min-width: 40px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(255, 255, 255, 0.4);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 12px;
                margin: 40px 0px 40px 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                min-height: 40px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.4);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                border: none;
            }
        """)

        self.scroll_area_content = QWidget()
        self.scroll_area_content.setMaximumWidth(850)
        self.main_layout = QVBoxLayout(self.scroll_area_content)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.setContentsMargins(40, 20, 40, 60)
        self.main_layout.setSpacing(32)
        
        self.scroll_area.setWidget(self.scroll_area_content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.scroll_area)

    def _clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self._clear_layout(item.layout())

    def _rebuild_dynamic_content(self):
        """Clears and reconstructs the form based on self.vm.mode"""
        self.setUpdatesEnabled(False)
        try:
            self._clear_layout(self.main_layout)

            mode = self.vm.mode
            if not mode:
                lbl = QLabel("No interview mode selected.")
                lbl.setStyleSheet("color: white;")
                self.main_layout.addWidget(lbl)
                return

            # ── Header ─────────────────────────────────────────────────────────────
            header_container = QWidget()
            header_layout = QVBoxLayout(header_container)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(8)
        
            hdr = self.ctx.ui.make_label(mode.title, role=LabelRole.H1.value)
            hdr.setStyleSheet("background: transparent; border: none; font-size: 28px; font-weight: 800; color: #FFFFFF;")
        
            sub = self.ctx.ui.make_label(mode.description, role=LabelRole.MUTED.value)
            sub.setStyleSheet("background: transparent; border: none; font-size: 14px; color: #9AA0A6;")
        
            header_layout.addWidget(hdr)
            header_layout.addWidget(sub)
            self.main_layout.addWidget(header_container)

            self.vm.field_widgets.clear()
        
            # ── Error Banner ───────────────────────────────────────────────────────
            self.error_banner = QLabel("")
            self.error_banner.setStyleSheet("color: #FF5252; background: rgba(255, 82, 82, 0.1); border-radius: 8px; padding: 10px; font-weight: bold;")
            self.error_banner.hide()
            self.main_layout.addWidget(self.error_banner)

            # ── Required Settings Panel ────────────────────────────────────────────
            if mode.required_inputs:
                req_frame = self._build_section_panel("Required Configuration", mode.required_inputs)
                self.main_layout.addWidget(req_frame)

            # ── Optional Settings Panel ────────────────────────────────────────────
            if mode.optional_inputs:
                opt_frame = self._build_section_panel("Optional Configuration", mode.optional_inputs)
                self.main_layout.addWidget(opt_frame)

            # ── Action Buttons ──────────────────────────────────────────────────────
            action_container = QWidget()
            action_layout = QHBoxLayout(action_container)
            action_layout.setContentsMargins(0, 40, 0, 0)
            action_layout.setSpacing(16)
        
            btn_back = self.ctx.ui.make_button("Cancel")
            btn_back.setStyleSheet(PREMIUM_BTN_SECONDARY_QSS)
            btn_back.clicked.connect(self.vm.go_back)
        
            btn_exec = self.ctx.ui.make_button(mode.primary_action_text)
            btn_exec.setStyleSheet(PREMIUM_BTN_PRIMARY_QSS)
            btn_exec.clicked.connect(self._on_submit)
        
            action_layout.addStretch()
            action_layout.addWidget(btn_back)
            action_layout.addWidget(btn_exec)

            self.main_layout.addWidget(action_container)
            self.main_layout.addStretch()
        
        finally:
            self.setUpdatesEnabled(True)

    def _build_section_panel(self, title: str, inputs: list) -> QWidget:
        container = QWidget()
        layout = QGridLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(32)

        title_lbl = self.ctx.ui.make_label(title, role=LabelRole.H2.value)
        title_lbl.setStyleSheet("background: transparent; border: none; font-size: 18px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(title_lbl, 0, 0, 1, 2)

        row = 1
        col = 0
        for field in inputs:
            # We want to span TextAreas across 2 columns
            from backend.domain.interview_mode import FieldType
            col_span = 2 if field.type == FieldType.TEXTAREA else 1
            
            widget = WidgetFactory.create(field, self.ctx, container)
            self.vm.field_widgets[field.id] = widget
            
            layout.addWidget(widget, row, col, 1, col_span)
            
            col += col_span
            if col >= 2:
                col = 0
                row += 1
                
        return container

    def _on_submit(self):
        self.error_banner.hide()
        success, errors = self.vm.submit()
        if not success:
            self.error_banner.setText("Validation Failed:\n" + "\n".join([f"• {e}" for e in errors]))
            self.error_banner.show()
            
            # Scroll to top to see errors
            self.scroll_area.verticalScrollBar().setValue(0)
