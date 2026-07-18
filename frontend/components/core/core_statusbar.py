"""
CoreStatusBar — bottom bar showing model, status, and clock.
Looks like a tmux status line.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QDateTime
from frontend.components.base.base_statusbar import BaseStatusbar
from frontend.engine import StyleEngine

class CoreStatusBar(BaseStatusbar):
    def __init__(self, engine: StyleEngine = None, parent=None):
        super().__init__(engine, parent)
        self.setObjectName("terminalStatusBar")
        self.setFixedHeight(24)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(0)

        # Left: status message
        self._status = QLabel(" READY ")
        
        bg_color = "#1f9900"
        fg_color = "#0a0a0a"
        if engine:
            bg_color = engine.resolver.resolve_color("colors.accent_dim")
            fg_color = engine.resolver.resolve_color("colors.text_inverse")
            
        self._status.setStyleSheet(
            f"color: {fg_color}; "
            f"background-color: {bg_color}; "
            f"font-size: 10px; padding: 0 6px;"
        )

        # Session info
        self._session = QLabel("  session: none  ")
        self._session.setObjectName("statusBarLabel")

        # Model info
        self._model = QLabel("  model: --  ")
        self._model.setObjectName("statusBarLabel")

        # Separator
        border_color = "#1f521f"
        if engine:
            border_color = engine.resolver.resolve_color("colors.border")
            
        sep1 = QLabel(" │ ")
        sep1.setStyleSheet(f"color: {border_color}; background: transparent; font-size: 10px;")

        sep2 = QLabel(" │ ")
        sep2.setStyleSheet(f"color: {border_color}; background: transparent; font-size: 10px;")

        # Clock (right)
        self._clock = QLabel()
        self._clock.setObjectName("statusBarLabelPrimary")
        self._update_clock()

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)

        layout.addWidget(self._status)
        layout.addWidget(self._session)
        layout.addWidget(sep1)
        layout.addWidget(self._model)
        layout.addStretch()
        layout.addWidget(sep2)
        layout.addWidget(self._clock)

    def _update_clock(self):
        now = QDateTime.currentDateTime()
        self._clock.setText(now.toString("  hh:mm:ss  "))

    def set_status(self, text: str, ok: bool = True):
        self._status.setText(f" {text.upper()} ")
        bg_color = "#1f9900" if ok else "#ff3333"
        fg_color = "#0a0a0a"
        if self._engine:
            bg_color = self._engine.resolver.resolve_color("colors.accent_dim" if ok else "colors.text_primary") # using primary or danger
        
        self._status.setStyleSheet(
            f"color: {fg_color}; background-color: {bg_color}; "
            f"font-size: 10px; padding: 0 6px;"
        )

    def set_model(self, model_name: str):
        self._model.setText(f"  model: {model_name}  ")

    def set_session(self, session_id: str):
        self._session.setText(f"  session: {session_id}  ")
