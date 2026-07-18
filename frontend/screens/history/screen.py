"""
History Screen — Command History / git log style.
Lists past interview sessions in tabular CLI format.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QSplitter, QScrollArea
)
from PySide6.QtCore import Qt

from frontend.core.base_screen import BaseScreen
from frontend.core.app_context import AppContext
from frontend.themes.base_theme import ButtonVariant
from .viewmodel import HistoryViewModel


# Simulated sessions
_SESSIONS = [
    {"id": "0xA3F2", "date": "2026-07-17", "role": "Software Engineer",     "company": "Google",   "type": "Technical",  "score": 82, "dur": "32m"},
    {"id": "0xB19C", "date": "2026-07-16", "role": "Backend Engineer",      "company": "Meta",     "type": "Behavioral", "score": 76, "dur": "28m"},
    {"id": "0xC04E", "date": "2026-07-15", "role": "ML Engineer",           "company": "OpenAI",   "type": "Technical",  "score": 90, "dur": "45m"},
    {"id": "0xD2A1", "date": "2026-07-14", "role": "System Design",         "company": "Netflix",  "type": "System Des", "score": 68, "dur": "40m"},
    {"id": "0xE3B7", "date": "2026-07-12", "role": "Frontend Engineer",     "company": "Stripe",   "type": "Behavioral", "score": 85, "dur": "22m"},
]


class HistoryScreen(BaseScreen):
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(ctx, parent)
        self.vm = HistoryViewModel(ctx, self)
        self._selected = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # ── Header ────────────────────────────────────────────────────
        hdr = self.ctx.ui.make_label("$ tellme history list", role="primary")
        root.addWidget(hdr)

        # ── Search + Filter bar ───────────────────────────────────────
        toolbar = QWidget()
        toolbar.setStyleSheet("background: transparent;")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(0, 0, 0, 0)
        self._search = self.ctx.ui.make_input(placeholder="filter sessions...", prompt="grep ")
        self._search.textChanged.connect(self._filter)
        tb_btn_all   = self.ctx.ui.make_button("ALL")
        tb_btn_tech  = self.ctx.ui.make_button("TECHNICAL")
        tb_btn_behav = self.ctx.ui.make_button("BEHAVIORAL")
        tb_btn_all.clicked.connect(lambda: self._filter(""))
        tb.addWidget(self._search, stretch=1)
        tb.addWidget(tb_btn_all)
        tb.addWidget(tb_btn_tech)
        tb.addWidget(tb_btn_behav)
        root.addWidget(toolbar)

        self._engine = self.ctx.theme_manager._engine
        self._resolver = self._engine.resolver if self._engine else None
        c_border = self._resolver.resolve_color("colors.border") if self._resolver else "#1f521f"

        # ── Splitter: list | detail ───────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {c_border}; }}"
        )

        # Left: session list
        list_win = self.ctx.ui.make_window("SESSIONS")
        self._list = QListWidget()
        self._list.setStyleSheet(
            "QListWidget { background: transparent; border: none; }"
            "QListWidget::item { padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }"
        )
        self._list.currentItemChanged.connect(self._on_select)
        self._populate_list(_SESSIONS)
        list_win.add_widget(self._list)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.ctx.ui.make_button("EXPORT"))
        btn_row.addWidget(self.ctx.ui.make_button("REMOVE", variant=ButtonVariant.DANGER))
        btn_row.addStretch()
        list_win.add_layout(btn_row)
        splitter.addWidget(list_win)

        # Right: detail pane
        self._detail_win = self.ctx.ui.make_window("DETAILS")
        self._detail_placeholder = self.ctx.ui.make_label(
            "  Select a session to view details.\n"
            "  Use arrow keys to navigate.", role="muted"
        )
        self._detail_win.add_widget(self._detail_placeholder)

        # Detail fields (hidden until selection)
        self._detail_content = QWidget()
        self._detail_content.setStyleSheet("background: transparent;")
        self._detail_content.setVisible(False)
        dc_layout = QVBoxLayout(self._detail_content)
        dc_layout.setContentsMargins(0, 0, 0, 0)
        dc_layout.setSpacing(4)

        self._d_fields: dict[str, QLabel] = {}
        for key in ["ID", "DATE", "ROLE", "COMPANY", "TYPE", "DURATION", "SCORE"]:
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            hl = QHBoxLayout(row)
            hl.setContentsMargins(0, 0, 0, 0)
            kl = self.ctx.ui.make_label(f"{key:<10}", role="muted")
            vl = self.ctx.ui.make_label("—")
            hl.addWidget(kl)
            hl.addWidget(vl, stretch=1)
            dc_layout.addWidget(row)
            self._d_fields[key] = vl

        dc_layout.addWidget(self.ctx.ui.make_separator())

        action_row = QHBoxLayout()
        action_row.addWidget(self.ctx.ui.make_button("OPEN REPORT"))
        action_row.addWidget(self.ctx.ui.make_button("EXPORT JSON"))
        action_row.addStretch()
        dc_layout.addLayout(action_row)
        dc_layout.addStretch()

        self._detail_win.add_widget(self._detail_content)
        splitter.addWidget(self._detail_win)
        splitter.setSizes([420, 580])

        root.addWidget(splitter, stretch=1)

    def _populate_list(self, sessions):
        self._list.clear()
        for s in sessions:
            text = (
                f"  {s['date']}  {s['id']}  "
                f"{s['role']:<22}  {s['type']:<12}  "
                f"score: {s['score']:3d}%  {s['dur']}"
            )
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, s)
            self._list.addItem(item)

    def _on_select(self, current, _):
        if not current:
            return
        s = current.data(Qt.ItemDataRole.UserRole)
        self._detail_placeholder.setVisible(False)
        self._detail_content.setVisible(True)
        self._d_fields["ID"].setText(s["id"])
        self._d_fields["DATE"].setText(s["date"])
        self._d_fields["ROLE"].setText(s["role"])
        self._d_fields["COMPANY"].setText(s["company"])
        self._d_fields["TYPE"].setText(s["type"])
        self._d_fields["DURATION"].setText(s["dur"])
        self._d_fields["SCORE"].setText(f"{s['score']}%")

    def _filter(self, text) -> None:
        query = str(text).lower()
        filtered = [
            s for s in _SESSIONS
            if query in str(s["role"]).lower()
            or query in str(s["type"]).lower()
            or query in str(s["company"]).lower()
        ]
        self._populate_list(filtered)

