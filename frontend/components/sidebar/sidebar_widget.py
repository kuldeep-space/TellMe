"""
TerminalSidebar — directory-tree style navigation panel.

Renders navigation as:

    TELLME v0.1
    ─────────────────
    > DASHBOARD
    ├── INTERVIEWS
    ├── HISTORY
    ├── REPORTS
    ├── MODELS
    └── SETTINGS

Active item has a bright left-border marker.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from typing import Optional
from frontend.components.base.base_sidebar import BaseSidebar
from frontend.engine import StyleEngine


# ── Tree prefix constants ──────────────────────────────────────────────
_ITEMS = [
    ("dashboard",        "HOME",              ">"),
    ("interview_config", "INTERVIEWS",        "├"),
    ("history",          "HISTORY",           "├"),
    ("report",           "REPORTS",           "├"),
    ("models",           "MODELS",            "├"),
    ("settings",         "SETTINGS",          "└"),
]


class _SidebarBtn(QPushButton):
    def __init__(self, prefix: str, label: str, parent=None):
        text = f"{prefix}── {label}"
        super().__init__(text, parent)
        self.setObjectName("sidebarButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setMinimumHeight(30)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


class TerminalSidebar(BaseSidebar):
    navigation_requested = Signal(str)

    def __init__(self, engine: Optional[StyleEngine] = None, parent=None):
        super().__init__(engine, parent)
        self.setObjectName("terminalSidebar")
        
        # We can resolve sidebar width from layout tokens if engine is available
        width = 220
        if engine:
            width = engine.resolver.resolve_int("layout.sidebar_width")
        self.setFixedWidth(width)
        
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self._buttons: dict[str, _SidebarBtn] = {}
        self._current = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ─────────────────────────────────────────────────────
        header = QWidget()
        bg_color = "#000000"
        fg_color = "#33ff00"
        muted_color = "#456145"
        border_color = "#1f521f"
        
        if self._engine:
            bg_color = self._engine.resolver.resolve_color("colors.background")
            fg_color = self._engine.resolver.resolve_color("colors.text_primary")
            muted_color = self._engine.resolver.resolve_color("colors.text_muted")
            border_color = self._engine.resolver.resolve_color("colors.border")
            
        header.setStyleSheet(f"background-color: {bg_color};")
        header.setFixedHeight(56)
        hl = QVBoxLayout(header)
        hl.setContentsMargins(12, 10, 12, 4)
        hl.setSpacing(0)

        title = QLabel("TELLME")
        title.setStyleSheet(
            f"color: {fg_color}; font-size: 14px; "
            f"font-weight: bold; background: transparent;"
        )
        sub = QLabel("terminal v0.1")
        sub.setStyleSheet(
            f"color: {muted_color}; font-size: 10px; background: transparent;"
        )
        hl.addWidget(title)
        hl.addWidget(sub)
        layout.addWidget(header)

        # ── Separator ──────────────────────────────────────────────────
        sep = QLabel("─" * 30)
        sep.setStyleSheet(
            f"color: {border_color}; font-size: 10px; "
            f"padding: 0 12px; background: transparent;"
        )
        layout.addWidget(sep)

        # ── Nav items ──────────────────────────────────────────────────
        nav_container = QWidget()
        nav_container.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(2)

        for screen_id, label, prefix in _ITEMS:
            btn = _SidebarBtn(prefix, label)
            btn.clicked.connect(lambda _, sid=screen_id: self._on_click(sid))
            nav_layout.addWidget(btn)
            self._buttons[screen_id] = btn

        nav_layout.addStretch()
        layout.addWidget(nav_container, stretch=1)

        # ── Footer ─────────────────────────────────────────────────────
        footer_sep = QLabel("─" * 30)
        footer_sep.setStyleSheet(
            f"color: {border_color}; font-size: 10px; "
            f"padding: 0 12px; background: transparent;"
        )
        layout.addWidget(footer_sep)

        footer = QLabel(" $ ready")
        footer.setStyleSheet(
            f"color: {muted_color}; font-size: 10px; "
            f"padding: 6px 12px; background: transparent;"
        )
        layout.addWidget(footer)

    def _on_click(self, screen_id: str):
        self._set_active(screen_id)
        self.navigation_requested.emit(screen_id)

    def _set_active(self, screen_id: str):
        for sid, btn in self._buttons.items():
            btn.setChecked(sid == screen_id)
        self._current = screen_id

    # Called from MainWindow after navigation
    def reflect_navigation(self, screen_id: str):
        self._set_active(screen_id)



