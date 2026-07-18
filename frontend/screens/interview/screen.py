"""
Interview Screen — Live Terminal Session.
Simulates a running shell session with live transcript,
ASCII waveform, token counter, and control dock.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen

from frontend.core.base_screen import BaseScreen
from frontend.core.app_context import AppContext
from frontend.themes.base_theme import ButtonVariant, BadgeLevel, LabelRole
import random
import math


class _WaveformWidget(QWidget):
    """Custom QPainter ASCII-style waveform — no OpenGL."""
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self._active = False
        self._phase  = 0.0
        self._bars: list[int] = [0] * 40
        self.setFixedHeight(36)
        self.setStyleSheet("background: transparent;")

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def set_active(self, active: bool):
        self._active = active
        if active:
            self._timer.start(80)
        else:
            self._timer.stop()
            self._bars = [0] * 40
            self.update()

    def _tick(self):
        self._phase += 0.3
        if self._active:
            self._bars = [
                int(14 * abs(math.sin(self._phase + i * 0.4)) * (0.4 + 0.6 * random.random()))
                for i in range(40)
            ]
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w = self.width()
        h = self.height()
        bar_w = max(1, w // 40)
        
        resolver = self.ctx.theme_manager._engine.resolver
        color_hex = resolver.resolve_color("colors.accent") if self._active else resolver.resolve_color("colors.border")
        color = QColor(color_hex)
        
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        for i, bar_h in enumerate(self._bars):
            x = i * bar_w
            y = h // 2 - bar_h // 2
            p.drawRect(x, y, max(1, bar_w - 1), max(1, bar_h))
        p.end()


class InterviewScreen(BaseScreen):
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(ctx, parent)
        from .viewmodel import InterviewViewModel
        self.vm = InterviewViewModel(ctx, self)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        resolver = self.ctx.theme_manager._engine.resolver

        # ── Top session info bar ───────────────────────────────────────
        session_bar = QWidget()
        session_bar.setStyleSheet(f"background: transparent;")
        session_bar.setFixedHeight(32)
        sb_layout = QHBoxLayout(session_bar)
        sb_layout.setContentsMargins(0, 0, 0, 0)

        self._session_id_lbl = self.ctx.ui.make_label("SESSION: none", role=LabelRole.MUTED.value)
        self._timer_lbl = self.ctx.ui.make_label("00:00:00", role=LabelRole.PRIMARY.value)
        self._token_lbl = self.ctx.ui.make_label("tokens: 0 / 4096", role=LabelRole.MUTED.value)
        self._status_badge = self.ctx.ui.make_badge(BadgeLevel.OFFLINE)

        sb_layout.addWidget(self._session_id_lbl)
        sb_layout.addStretch()
        sb_layout.addWidget(self._token_lbl)
        sb_layout.addSpacing(16)
        sb_layout.addWidget(self.ctx.ui.make_label("STATUS:", role=LabelRole.MUTED.value))
        sb_layout.addWidget(self._status_badge)
        sb_layout.addSpacing(16)
        sb_layout.addWidget(self._timer_lbl)
        root.addWidget(session_bar)

        # ── Main splitter: transcript | controls ───────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {resolver.resolve_color('colors.border')}; width: 1px; }}"
        )

        # Left: transcript
        left = self.ctx.ui.make_window("TRANSCRIPT")
        self._transcript = self.ctx.ui.make_textarea(read_only=True)
        self._transcript.setMinimumWidth(400)
        left.add_widget(self._transcript)

        # Prompt row
        prompt_row = QHBoxLayout()
        self._prompt_input = self.ctx.ui.make_input("Type your answer and press Enter...", "your response > ")
        self._send_btn = self.ctx.ui.make_button("SEND", ButtonVariant.PRIMARY)
        self._send_btn.clicked.connect(self._on_send)
        prompt_row.addWidget(self._prompt_input, stretch=1)
        prompt_row.addWidget(self._send_btn)
        left.add_layout(prompt_row)

        splitter.addWidget(left)

        # Right: controls + waveform + notes
        right_container = QWidget()
        right_container.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(8)

        # Waveform
        wave_win = self.ctx.ui.make_window("AUDIO INPUT")
        self._waveform = _WaveformWidget(self.ctx)
        self._mic_label = self.ctx.ui.make_label("[ MIC: OFF ]", role=LabelRole.MUTED.value)
        wave_win.add_widget(self._waveform)
        wave_win.add_widget(self._mic_label)
        right_layout.addWidget(wave_win)

        # Controls
        ctrl_win = self.ctx.ui.make_window("CONTROLS")
        ctrl_col = QVBoxLayout()
        ctrl_col.setSpacing(4)

        self._mic_btn    = self.ctx.ui.make_button("UNMUTE MIC", ButtonVariant.PRIMARY)
        self._pause_btn  = self.ctx.ui.make_button("PAUSE", ButtonVariant.WARNING)
        self._end_btn    = self.ctx.ui.make_button("END SESSION", ButtonVariant.DANGER)

        self._mic_btn.clicked.connect(self._toggle_mic)
        self._pause_btn.clicked.connect(self._pause)
        self._end_btn.clicked.connect(self._end_session)

        ctrl_col.addWidget(self._mic_btn)
        ctrl_col.addWidget(self._pause_btn)
        ctrl_col.addWidget(self.ctx.ui.make_separator("·"))
        ctrl_col.addWidget(self._end_btn)
        ctrl_win.add_layout(ctrl_col)
        right_layout.addWidget(ctrl_win)

        # Notes
        notes_win = self.ctx.ui.make_window("NOTES")
        self._notes = self.ctx.ui.make_textarea()
        self._notes.setPlaceholderText("# press ctrl+s to save notes...")
        notes_win.add_widget(self._notes)
        right_layout.addWidget(notes_win, stretch=1)

        splitter.addWidget(right_container)
        splitter.setSizes([680, 320])

        root.addWidget(splitter, stretch=1)

        # Session timer
        self._elapsed = 0
        self._run_timer = QTimer(self)
        self._run_timer.timeout.connect(self._tick_timer)

    def _toggle_mic(self):
        resolver = self.ctx.theme_manager._engine.resolver
        self.vm.mic_active = not self.vm.mic_active
        if self.vm.mic_active:
            self._waveform.set_active(True)
            self._mic_label.setText("[ MIC: ON  ]")
            self._mic_label.setStyleSheet(
                f"color: {resolver.resolve_color('status.success')}; background: transparent; font-family: {resolver.resolve_str('typography.family_mono')}; font-size: {resolver.resolve_str('typography.size_sm')};"
            )
            # Some buttons might not have set_label, just setText
            if hasattr(self._mic_btn, 'set_label'):
                self._mic_btn.set_label("MUTE MIC")
            else:
                self._mic_btn.setText("MUTE MIC")
        else:
            self._waveform.set_active(False)
            self._mic_label.setText("[ MIC: OFF ]")
            self._mic_label.setStyleSheet(
                f"color: {resolver.resolve_color('colors.text_muted')}; background: transparent; font-family: {resolver.resolve_str('typography.family_mono')}; font-size: {resolver.resolve_str('typography.size_sm')};"
            )
            if hasattr(self._mic_btn, 'set_label'):
                self._mic_btn.set_label("UNMUTE MIC")
            else:
                self._mic_btn.setText("UNMUTE MIC")

    def _pause(self):
        if self._run_timer.isActive():
            self._run_timer.stop()
            if hasattr(self._pause_btn, 'set_label'):
                self._pause_btn.set_label("RESUME")
            else:
                self._pause_btn.setText("RESUME")
            self._status_badge.set_level(BadgeLevel.WARN)
        else:
            self._run_timer.start(1000)
            if hasattr(self._pause_btn, 'set_label'):
                self._pause_btn.set_label("PAUSE")
            else:
                self._pause_btn.setText("PAUSE")
            self._status_badge.set_level(BadgeLevel.BUSY)

    def _end_session(self):
        resolver = self.ctx.theme_manager._engine.resolver
        self._run_timer.stop()
        self._waveform.set_active(False)
        self._status_badge.set_level(BadgeLevel.OK)
        if hasattr(self._transcript, 'append_line'):
            self._transcript.append_line(
                "\n[SESSION ENDED]  Generating diagnostics report...",
                resolver.resolve_color("colors.accent")
            )
        self.ctx.navigation_controller.push("report")

    def _on_send(self):
        resolver = self.ctx.theme_manager._engine.resolver
        text = self._prompt_input.text().strip()
        if not text:
            return
        if hasattr(self._transcript, 'append_line'):
            self._transcript.append_line(f"\n> {text}", resolver.resolve_color("colors.text_primary"))
            self._transcript.append_line("  [PROCESSING...]", resolver.resolve_color("colors.text_muted"))
        self._prompt_input.clear()

    def _tick_timer(self):
        self._elapsed += 1
        h = self._elapsed // 3600
        m = (self._elapsed % 3600) // 60
        s = self._elapsed % 60
        self._timer_lbl.setText(f"{h:02}:{m:02}:{s:02}")

    def on_enter(self):
        super().on_enter()
        resolver = self.ctx.theme_manager._engine.resolver
        self._elapsed = 0
        self._run_timer.start(1000)
        self._status_badge.set_level(BadgeLevel.BUSY)
        self._session_id_lbl.setText("SESSION: 0x" + __import__("uuid").uuid4().hex[:8].upper())
        self._transcript.clear()
        
        if hasattr(self._transcript, 'append_line'):
            self._transcript.append_line("TellMe Interview Session — Initialized", resolver.resolve_color("colors.accent"))
            self._transcript.append_line("─" * 60 + "\n", resolver.resolve_color("colors.border"))
            self._transcript.append_line(
                "[AI]  Hello! I will be your interviewer today.\n"
                "      Let's start with a brief introduction.\n"
                "      Tell me about yourself and your background.\n",
                resolver.resolve_color("colors.text_secondary")
            )

    def on_leave(self):
        super().on_leave()
        self._run_timer.stop()
        self._waveform.set_active(False)
