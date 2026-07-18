"""
IndustrialStatusBar — Recessed bar at the bottom with LED status.
"""
from PySide6.QtWidgets import QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QDateTime
from frontend.components.base.base_statusbar import BaseStatusbar
from frontend.engine import StyleEngine
from frontend.components.industrial.led_indicator import LedIndicator
from frontend.components.industrial.steel_panel import SteelPanel

class IndustrialStatusBar(BaseStatusbar):
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(engine, parent)
        self.setFixedHeight(32)
        
        # In Industrial, we might want the status bar to look like an inset panel
        # We can do this with QSS or by wrapping content in an inset panel.
        # For simplicity, we just use a styled layout.
        self.setStyleSheet(
            f"QStatusBar {{ background: {engine.resolver.resolve_color('colors.surface')}; border-top: 2px solid {engine.resolver.resolve_color('colors.border')}; }}"
        )
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(12)
        
        self._led = LedIndicator(engine, "led.online_color")
        self._status = QLabel("SYSTEM ONLINE")
        self._status.setStyleSheet(f"color: {engine.resolver.resolve_color('colors.text_primary')}; font-weight: bold; font-size: 11px;")
        
        self._session = QLabel("SESSION: --")
        self._session.setStyleSheet(f"color: {engine.resolver.resolve_color('colors.text_muted')}; font-size: 11px;")
        
        self._model = QLabel("MODEL: --")
        self._model.setStyleSheet(f"color: {engine.resolver.resolve_color('colors.text_muted')}; font-size: 11px;")
        
        self._clock = QLabel()
        self._clock.setStyleSheet(f"color: {engine.resolver.resolve_color('colors.text_secondary')}; font-size: 11px;")
        
        layout.addWidget(self._led)
        layout.addWidget(self._status)
        layout.addWidget(self._session)
        layout.addStretch()
        layout.addWidget(self._model)
        layout.addWidget(self._clock)
        
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()
        
    def _update_clock(self):
        self._clock.setText(QDateTime.currentDateTime().toString("hh:mm:ss"))
        
    def set_status(self, text: str, ok: bool = True):
        self._status.setText(text.upper())
        self._led._color_token = "led.online_color" if ok else "led.error_color"
        self._led.update()
        
    def set_model(self, model_name: str):
        self._model.setText(f"MODEL: {model_name}")
        
    def set_session(self, session_id: str):
        self._session.setText(f"SESSION: {session_id}")
