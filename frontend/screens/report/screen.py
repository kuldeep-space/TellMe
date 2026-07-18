"""
Report Screen — Diagnostics Report, skill analysis using ASCII bars.
Resembles generated CLI diagnostic output.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
)
from PySide6.QtCore import Qt
from frontend.core.base_screen import BaseScreen
from frontend.core.app_context import AppContext
from frontend.themes.base_theme import BadgeLevel
from .viewmodel import ReportViewModel

_SAMPLE = {
    "id": "0xA3F2",
    "date": "2026-07-17",
    "role": "Software Engineer",
    "company": "Google",
    "duration": "32m",
    "overall": 82,
    "categories": {
        "Communication":    88,
        "Technical Depth":  78,
        "Problem Solving":  85,
        "Culture Fit":      80,
        "Confidence":       79,
    },
    "strengths": [
        "Clear verbal communication with structured answers",
        "Good use of STAR method in behavioral questions",
        "Demonstrated depth in distributed systems knowledge",
    ],
    "improvements": [
        "Struggled with complexity analysis — practice Big-O notation",
        "Verbose in system design — be more concise",
        "Low engagement on follow-up probing questions",
    ],
    "recommendations": [
        "$ leetcode practice --tag 'graphs,dp' --difficulty medium",
        "$ review system-design/consistent-hashing.md",
        "$ mock-interview --focus 'follow-up questions' --n 5",
    ],
}


class ReportScreen(BaseScreen):
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(ctx, parent)
        self.vm = ReportViewModel(ctx, self)
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        main = QVBoxLayout(container)
        main.setContentsMargins(12, 12, 12, 12)
        main.setSpacing(8)

        # Header
        hdr = self.ctx.ui.make_label(f"$ tellme report view --id {_SAMPLE['id']}", role="primary")
        main.addWidget(hdr)
        main.addWidget(self.ctx.ui.make_label(
            f"  date: {_SAMPLE['date']}  |  role: {_SAMPLE['role']}  |  company: {_SAMPLE['company']}  |  duration: {_SAMPLE['duration']}",
            role="muted"
        ))
        main.addWidget(self.ctx.ui.make_separator())

        # Top row: Overall + Actions
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        overall_win = self.ctx.ui.make_window("OVERALL SCORE")
        score = _SAMPLE["overall"]
        badge = BadgeLevel.OK if score >= 80 else BadgeLevel.WARN if score >= 60 else BadgeLevel.ERR
        overall_bar = self.ctx.ui.make_progress(30)
        overall_bar.set_value(score)
        
        score_big = self.ctx.ui.make_label(f"  {score} / 100", role="primary")
        
        overall_win.add_widget(score_big)
        overall_win.add_widget(overall_bar)
        overall_win.add_widget(self.ctx.ui.make_badge(badge))
        top_row.addWidget(overall_win, stretch=1)

        actions_win = self.ctx.ui.make_window("ACTIONS")
        actions_win.add_widget(self.ctx.ui.make_button("EXPORT PDF"))
        actions_win.add_widget(self.ctx.ui.make_button("EXPORT JSON"))
        actions_win.add_widget(self.ctx.ui.make_button("SHARE LINK"))
        top_row.addWidget(actions_win)
        main.addLayout(top_row)

        # Category Scores
        cat_win = self.ctx.ui.make_window("CATEGORY SCORES")
        for cat, val in _SAMPLE["categories"].items():
            row = QHBoxLayout()
            row.setSpacing(8)
            k = self.ctx.ui.make_label(f"{cat:<20}", role="secondary")
            bar = self.ctx.ui.make_progress(20, show_percent=True)
            bar.set_value(val)
            row.addWidget(k)
            row.addWidget(bar)
            row.addStretch()
            cat_win.add_layout(row)
        main.addWidget(cat_win)

        # Strengths / Improvements side by side
        sw_row = QHBoxLayout()
        sw_row.setSpacing(8)

        str_win = self.ctx.ui.make_window("STRENGTHS")
        for s in _SAMPLE["strengths"]:
            lbl = self.ctx.ui.make_label(f"  [+]  {s}", role="success")
            lbl.setWordWrap(True)
            str_win.add_widget(lbl)
        sw_row.addWidget(str_win, stretch=1)

        imp_win = self.ctx.ui.make_window("IMPROVEMENTS")
        for i in _SAMPLE["improvements"]:
            lbl = self.ctx.ui.make_label(f"  [-]  {i}", role="warning")
            lbl.setWordWrap(True)
            imp_win.add_widget(lbl)
        sw_row.addWidget(imp_win, stretch=1)
        main.addLayout(sw_row)

        # Recommendations
        rec_win = self.ctx.ui.make_window("RECOMMENDATIONS")
        rec_win.add_widget(self.ctx.ui.make_label("  Run these commands to address identified weaknesses:", role="muted"))
        rec_win.add_widget(self.ctx.ui.make_separator())
        for rec in _SAMPLE["recommendations"]:
            lbl = self.ctx.ui.make_label(f"  {rec}", role="primary")
            rec_win.add_widget(lbl)
        main.addWidget(rec_win)

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
