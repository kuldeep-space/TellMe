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
        scroll.setStyleSheet("background: transparent;")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(40, 40, 40, 40)
        scroll_layout.setSpacing(32)

        # ── Hero Section ────────────────────────────────────────────────
        hero_layout = QVBoxLayout()
        hero_layout.setSpacing(8)
        
        greeting = self.ctx.ui.make_label("Start Preparation", role=LabelRole.H1.value)
        subtitle = self.ctx.ui.make_label("Choose an interview mode to begin your AI interview.", role=LabelRole.MUTED.value)
        
        hero_layout.addWidget(greeting)
        hero_layout.addWidget(subtitle)
        hero_layout.addSpacing(16)
        
        scroll_layout.addLayout(hero_layout)

        # ── Dynamic Categories ──────────────────────────────────────────
        categories = self.vm.get_interview_categories()
        
        for category, modes in categories.items():
            cat_layout = QVBoxLayout()
            cat_layout.setSpacing(16)
            
            cat_title = self.ctx.ui.make_label(category, role=LabelRole.H2.value)
            cat_layout.addWidget(cat_title)
            
            # Grid for cards
            grid = QGridLayout()
            grid.setSpacing(16)
            
            col = 0
            row = 0
            for mode in modes:
                card = self._build_mode_card(mode)
                grid.addWidget(card, row, col)
                col += 1
                if col > 1: # 2 columns max for better readability at desktop size
                    col = 0
                    row += 1
            
            cat_layout.addLayout(grid)
            scroll_layout.addLayout(cat_layout)
            scroll_layout.addSpacing(24)

        # ── Recent Interviews Table ──────────────────────────────────────
        table_layout = QVBoxLayout()
        table_layout.setSpacing(16)
        
        table_title = self.ctx.ui.make_label("Recent Interviews", role=LabelRole.H2.value)
        table_layout.addWidget(table_title)
        
        # We will use a QTableWidget or custom widget for the table.
        # For now, a styled QFrame acting as an empty state.
        from PySide6.QtWidgets import QFrame
        table_frame = QFrame()
        
        bg_color = self.ctx.ui._engine.resolver.resolve_color("colors.surface")
        border_color = self.ctx.ui._engine.resolver.resolve_color("colors.border")
        radius = self.ctx.ui._engine.resolver.resolve_str("radius.md")
        
        table_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {radius}px;
            }}
        """)
        table_frame.setMinimumHeight(200)
        
        tf_layout = QVBoxLayout(table_frame)
        empty_lbl = self.ctx.ui.make_label("No recent interviews found.", role=LabelRole.MUTED.value)
        empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tf_layout.addWidget(empty_lbl)
        
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
        radius = self.ctx.ui._engine.resolver.resolve_str("radius.md")
        
        # Flat styling with rounded corners, no neumorphism
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {radius}px;
            }}
            QFrame:hover {{
                background-color: {hover_color};
                border: 1px solid #555555;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)
        
        # Header (Icon + Title)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add Title
        title_lbl = self.ctx.ui.make_label(mode.title, role=LabelRole.H2.value)
        title_lbl.setStyleSheet(title_lbl.styleSheet() + "border: none; background: transparent;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        card_layout.addLayout(header_layout)
        
        # Description
        desc_lbl = self.ctx.ui.make_label(mode.description, role=LabelRole.MUTED.value)
        desc_lbl.setStyleSheet(desc_lbl.styleSheet() + "border: none; background: transparent;")
        desc_lbl.setWordWrap(True)
        desc_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        card_layout.addWidget(desc_lbl)
        
        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 8, 0, 0)
        
        duration_lbl = self.ctx.ui.make_label(f"⏱ {mode.estimated_duration}", role=LabelRole.MUTED.value)
        duration_lbl.setStyleSheet(duration_lbl.styleSheet() + "border: none; background: transparent;")
        footer_layout.addWidget(duration_lbl)
        
        footer_layout.addStretch()
        
        select_btn = self.ctx.ui.make_button("Select", variant=ButtonVariant.SECONDARY)
        select_btn.clicked.connect(lambda _, m_id=mode.id: self.vm.start_interview_mode(m_id))
        footer_layout.addWidget(select_btn)
        
        card_layout.addLayout(footer_layout)
        return card
