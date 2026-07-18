"""
Dashboard Screen — Modular AI Interview Platform Launcher.

Presents dynamically registered interview modes categorized logically.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt

from frontend.core.base_screen import BaseScreen
from frontend.core.app_context import AppContext
from frontend.themes.base_theme import ButtonVariant, LabelRole
from .viewmodel import InterviewModesViewModel


class InterviewModesScreen(BaseScreen):
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(ctx, parent)
        self.vm = InterviewModesViewModel(ctx, self)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Scroll Area for dynamic content ──────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("""
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
                background: rgba(255, 255, 255, 0.3);
                min-width: 40px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(255, 255, 255, 0.5);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
                border: none;
            }
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll_layout.setContentsMargins(40, 40, 40, 40)
        scroll_layout.setSpacing(64)

        # ── Header ──────────────────────────────────────────────────────
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        greeting = self.ctx.ui.make_label("Start Preparation", role=LabelRole.H1.value)
        subtitle = self.ctx.ui.make_label("Choose an interview mode to begin your AI interview.", role=LabelRole.MUTED.value)
        
        header_layout.addWidget(greeting)
        header_layout.addWidget(subtitle)
        
        scroll_layout.addLayout(header_layout)

        # ── Interview Mode Cards ─────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(24)
        
        all_modes = self.vm.get_all_modes()
        
        col = 0
        row = 0
        for mode in all_modes:
            card = self._build_mode_card(mode)
            card.setMinimumWidth(280)
            card.setMaximumWidth(340)
            grid.addWidget(card, row, col)
            col += 1
            if col > 2: # 3 columns max
                col = 0
                row += 1
                
        grid_wrapper = QHBoxLayout()
        grid_wrapper.addStretch()
        grid_wrapper.addLayout(grid)
        grid_wrapper.addStretch()
                
        scroll_layout.addLayout(grid_wrapper)

        # ── Recent Interviews Table ──────────────────────────────────────
        table_layout = QVBoxLayout()
        table_layout.setSpacing(16)
        
        table_title = self.ctx.ui.make_label("Recent Interviews", role=LabelRole.H2.value)
        table_layout.addWidget(table_title)
        
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QFrame
        
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["Date", "Interview Name", "Mode", "Performance", "Report"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setMinimumHeight(120)
        
        # In the future, we will populate this with actual history.
        # For now, it will just show the empty state message.
        empty_lbl = self.ctx.ui.make_label("No interviews yet. Start your first interview.", role=LabelRole.MUTED.value)
        empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # We can stack the empty label over the table or just show it if rowCount == 0
        table_frame = QFrame()
        tf_layout = QVBoxLayout(table_frame)
        tf_layout.setContentsMargins(0, 0, 0, 0)
        tf_layout.addWidget(table)
        
        # If no rows, overlay the empty state
        if table.rowCount() == 0:
            tf_layout.addWidget(empty_lbl)
            table.hide()
        
        table_layout.addWidget(table_frame)
        scroll_layout.addLayout(table_layout)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        root.addWidget(scroll)

    def _build_mode_card(self, mode) -> QWidget:
        """Builds a premium card for an individual interview mode."""
        from PySide6.QtWidgets import QFrame
        
        card = QFrame()
        
        bg_color = self.ctx.ui._engine.resolver.resolve_color("colors.surface")
        border_color = self.ctx.ui._engine.resolver.resolve_color("colors.border")
        hover_color = self.ctx.ui._engine.resolver.resolve_color("colors.surface_hover")
        radius = self.ctx.ui._engine.resolver.resolve_str("radius.lg")
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {radius}px;
            }}
            QFrame:hover {{
                background-color: {hover_color};
                border: 1px solid #999999;
            }}
        """)
        
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(12)
        
        # Header (Icon + Title)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        # We can use a label for the icon, or just the title if no actual SVG is easily available.
        # But we have `mode.icon` which could map to a string or icon. We will just use the text.
        title_lbl = self.ctx.ui.make_label(mode.title, role=LabelRole.H2.value)
        title_lbl.setStyleSheet(title_lbl.styleSheet() + "border: none; background: transparent;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        card_layout.addLayout(header_layout)
        
        # Description
        desc_lbl = self.ctx.ui.make_label(mode.description, role=LabelRole.MUTED.value)
        desc_lbl.setStyleSheet(desc_lbl.styleSheet() + "border: none; background: transparent;")
        desc_lbl.setWordWrap(True)
        desc_lbl.setMaximumWidth(240)
        card_layout.addWidget(desc_lbl)
        
        card_layout.addSpacing(8)
        
        # Features List
        features_layout = QVBoxLayout()
        features_layout.setSpacing(6)
        
        # Assume mode.feature_list exists now
        features = getattr(mode, "feature_list", [])
        for feature in features:
            f_lbl = self.ctx.ui.make_label(f"• {feature}", role=LabelRole.PRIMARY.value)
            f_lbl.setStyleSheet(f_lbl.styleSheet() + "border: none; background: transparent; color: #a0a0a0;")
            features_layout.addWidget(f_lbl)
            
        card_layout.addLayout(features_layout)
        
        # Stretch pushes the button to the bottom, ensuring equal height cards across row
        card_layout.addStretch(1)
        
        # Button
        button_text = getattr(mode, "button_text", "Let's Start →")
        select_btn = self.ctx.ui.make_button(button_text, variant=ButtonVariant.PRIMARY)
        # Ensure it spans full width
        select_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        select_btn.clicked.connect(lambda _, m_id=mode.id: self.vm.start_interview_mode(m_id))
        
        card_layout.addWidget(select_btn)
        
        return card
