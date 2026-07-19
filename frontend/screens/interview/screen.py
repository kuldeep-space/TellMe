"""
Interview Screen — Live Terminal Session.
Simulates a running shell session with live transcript,
AI interviewer mascot, token counter, and control dock.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen

from frontend.core.base_screen import BaseScreen
from frontend.core.app_context import AppContext
from frontend.themes.base_theme import ButtonVariant, BadgeLevel, LabelRole
from frontend.components.mascot import MascotWidget, MascotEmotion, MascotActivity, MascotPresence, MascotEventType
import random
import math
import time


class _WaveformWidget(QWidget):
    """Custom QPainter waveform — compact audio indicator."""
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self._active = False
        self._phase  = 0.0
        self._bars: list[int] = [0] * 28
        self.setFixedHeight(24)
        self.setStyleSheet("background: transparent;")

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def set_active(self, active: bool):
        self._active = active
        if active:
            self._timer.start(80)
        else:
            self._timer.stop()
            self._bars = [0] * 28
            self.update()

    def _tick(self):
        self._phase += 0.3
        if self._active:
            self._bars = [
                int(10 * abs(math.sin(self._phase + i * 0.4)) * (0.4 + 0.6 * random.random()))
                for i in range(28)
            ]
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w = self.width()
        h = self.height()
        bar_w = max(1, w // 28)

        resolver = self.ctx.theme_manager._engine.resolver
        color_hex = (
            resolver.resolve_color("colors.accent")
            if self._active else
            resolver.resolve_color("colors.border")
        )
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
        session_bar.setStyleSheet("background: transparent;")
        session_bar.setFixedHeight(32)
        sb_layout = QHBoxLayout(session_bar)
        sb_layout.setContentsMargins(0, 0, 0, 0)

        self._session_id_lbl = self.ctx.ui.make_label("SESSION: none", role=LabelRole.MUTED.value)
        self._timer_lbl      = self.ctx.ui.make_label("00:00:00",        role=LabelRole.PRIMARY.value)
        self._token_lbl      = self.ctx.ui.make_label("tokens: 0 / 4096", role=LabelRole.MUTED.value)
        self._status_badge   = self.ctx.ui.make_badge(BadgeLevel.OFFLINE)

        sb_layout.addWidget(self._session_id_lbl)
        sb_layout.addStretch()
        sb_layout.addWidget(self._token_lbl)
        sb_layout.addSpacing(16)
        sb_layout.addWidget(self.ctx.ui.make_label("STATUS:", role=LabelRole.MUTED.value))
        sb_layout.addWidget(self._status_badge)
        sb_layout.addSpacing(16)
        sb_layout.addWidget(self._timer_lbl)
        root.addWidget(session_bar)

        # ── Main splitter: transcript | mascot + controls ──────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {resolver.resolve_color('colors.border')}; width: 1px; }}"
        )

        # ── LEFT: transcript ───────────────────────────────────────────
        left = self.ctx.ui.make_window("TRANSCRIPT")
        self._transcript = self.ctx.ui.make_textarea(read_only=True)
        self._transcript.setMinimumWidth(380)
        left.add_widget(self._transcript)

        # Prompt row
        prompt_row = QHBoxLayout()
        self._prompt_input = self.ctx.ui.make_input(
            "Type your answer and press Enter...", "your response > "
        )
        self._send_btn = self.ctx.ui.make_button("SEND", ButtonVariant.PRIMARY)
        self._send_btn.clicked.connect(self._on_send)
        prompt_row.addWidget(self._prompt_input, stretch=1)
        prompt_row.addWidget(self._send_btn)
        left.add_layout(prompt_row)

        splitter.addWidget(left)

        # ── RIGHT: mascot panel ────────────────────────────────────────
        right_container = QWidget()
        right_container.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(8)

        # Mascot character frame
        mascot_frame = self.ctx.ui.make_window("AI INTERVIEWER")
        self._mascot = MascotWidget()
        mascot_frame.add_widget(self._mascot)

        # Compact waveform + mic label below mascot
        audio_row = QHBoxLayout()
        audio_row.setContentsMargins(0, 0, 0, 0)
        self._waveform  = _WaveformWidget(self.ctx)
        self._mic_label = self.ctx.ui.make_label("MIC: OFF", role=LabelRole.MUTED.value)
        audio_row.addWidget(self._waveform, stretch=1)
        audio_row.addSpacing(8)
        audio_row.addWidget(self._mic_label)
        mascot_frame.add_layout(audio_row)

        right_layout.addWidget(mascot_frame, stretch=1)

        # Controls
        ctrl_win = self.ctx.ui.make_window("CONTROLS")
        ctrl_col = QVBoxLayout()
        ctrl_col.setSpacing(4)

        self._mic_btn   = self.ctx.ui.make_button("UNMUTE MIC",  ButtonVariant.PRIMARY)
        self._pause_btn = self.ctx.ui.make_button("PAUSE",        ButtonVariant.WARNING)
        self._end_btn   = self.ctx.ui.make_button("END SESSION",  ButtonVariant.DANGER)

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
        splitter.setSizes([660, 340])

        root.addWidget(splitter, stretch=1)

        # Session timers
        self._elapsed   = 0
        self._run_timer = QTimer(self)
        self._run_timer.timeout.connect(self._tick_timer)

    # ─────────────────────────────────────────────────────────
    # Mascot state & Streaming simulation
    # ─────────────────────────────────────────────────────────

    def _start_streaming_response(self, text: str):
        """Streams text word-by-word onto transcript and emits chunks to Mascot."""
        if hasattr(self, "_stream_timer") and self._stream_timer.isActive():
            self._stream_timer.stop()

        self._stream_words = text.split(" ")
        self._stream_index = 0

        # Notify speaking started
        self._mascot.controller.handle_event(MascotEventType.AI_SPEECH_STARTED)

        resolver = self.ctx.theme_manager._engine.resolver
        if hasattr(self._transcript, 'append_line'):
            self._transcript.append_line("\n[AI] ", resolver.resolve_color("colors.accent"))

        self._stream_timer = QTimer(self)
        self._stream_timer.timeout.connect(self._stream_tick)
        self._stream_timer.start(160)

    def _stream_tick(self):
        if self._stream_index >= len(self._stream_words):
            self._stream_timer.stop()
            self._mascot.controller.handle_event(MascotEventType.AI_SPEECH_ENDED)
            return

        word = self._stream_words[self._stream_index]
        self._stream_index += 1

        if hasattr(self._transcript, 'insertPlainText'):
            self._transcript.insertPlainText(word + " ")
            self._transcript.ensureCursorVisible()

        # Emit chunk to mascot resolver
        self._mascot.controller.handle_event(MascotEventType.AI_TEXT_CHUNK, {"text": word})

    # ─────────────────────────────────────────────────────────
    # Control handlers
    # ─────────────────────────────────────────────────────────

    def _toggle_mic(self):
        resolver = self.ctx.theme_manager._engine.resolver
        self.vm.mic_active = not self.vm.mic_active
        if self.vm.mic_active:
            self._waveform.set_active(True)
            self._mic_label.setText("MIC: ON")
            self._mic_label.setStyleSheet(
                f"color: {resolver.resolve_color('status.success')}; background: transparent;"
            )
            if hasattr(self._mic_btn, 'set_label'):
                self._mic_btn.set_label("MUTE MIC")
            else:
                self._mic_btn.setText("MUTE MIC")
            
            # User speech started
            self._mascot.controller.handle_event(MascotEventType.SPEECH_STARTED)
            self._mic_start_time = time.time()
        else:
            self._waveform.set_active(False)
            self._mic_label.setText("MIC: OFF")
            self._mic_label.setStyleSheet(
                f"color: {resolver.resolve_color('colors.text_muted')}; background: transparent;"
            )
            if hasattr(self._mic_btn, 'set_label'):
                self._mic_btn.set_label("UNMUTE MIC")
            else:
                self._mic_btn.setText("UNMUTE MIC")
            
            # User speech ended
            self._mascot.controller.handle_event(MascotEventType.SPEECH_ENDED)
            
            # Quick toggle (VAD simulation / audio quality check)
            duration = time.time() - getattr(self, "_mic_start_time", 0.0)
            if duration < 1.4:
                # Triggers low confidence concerned state
                self._mascot.controller.handle_event(MascotEventType.LOW_CONFIDENCE)
                self._start_streaming_response("😕 I noticed some microphone noise or stutter. Could you please repeat that? 🙁")
            else:
                # Normal speech response loop
                self._mascot.controller.handle_event(MascotEventType.THINKING_STARTED)
                QTimer.singleShot(1500, lambda: self._start_streaming_response("🙂 That is an interesting point. 🤔 Tell me more about your recent project experience. 😊"))

    def _pause(self):
        if self._run_timer.isActive():
            self._run_timer.stop()
            if hasattr(self._pause_btn, 'set_label'):
                self._pause_btn.set_label("RESUME")
            else:
                self._pause_btn.setText("RESUME")
            self._status_badge.set_level(BadgeLevel.WARN)
            
            # Idle/pause sequence
            self._mascot.controller.handle_event(MascotEventType.SPEECH_ENDED)
        else:
            self._run_timer.start(1000)
            if hasattr(self._pause_btn, 'set_label'):
                self._pause_btn.set_label("PAUSE")
            else:
                self._pause_btn.setText("PAUSE")
            self._status_badge.set_level(BadgeLevel.BUSY)
            
            # Listening/resume sequence
            self._mascot.controller.handle_event(MascotEventType.SPEECH_STARTED)

    def _end_session(self):
        resolver = self.ctx.theme_manager._engine.resolver
        self._run_timer.stop()
        self._waveform.set_active(False)
        self._status_badge.set_level(BadgeLevel.OK)
        
        # End interview sequence
        self._mascot.controller.handle_event(MascotEventType.EXPLICIT_EMOTION, {"emotion": MascotEmotion.HAPPY})
        
        if hasattr(self._transcript, 'append_line'):
            self._transcript.append_line(
                "\n[SESSION ENDED]  Generating diagnostics report...",
                resolver.resolve_color("colors.accent")
            )
        QTimer.singleShot(1200, lambda: self.ctx.navigation_controller.push("report"))

    def _on_send(self):
        resolver = self.ctx.theme_manager._engine.resolver
        text = self._prompt_input.text().strip()
        if not text:
            return
        if hasattr(self._transcript, 'append_line'):
            self._transcript.append_line(f"\n> {text}", resolver.resolve_color("colors.text_primary"))
            self._transcript.append_line("  [PROCESSING...]", resolver.resolve_color("colors.text_muted"))
        self._prompt_input.clear()

        # Emit thinking event
        self._mascot.controller.handle_event(MascotEventType.THINKING_STARTED)
        
        # Sentiment response mapper
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["great", "excellent", "perfect", "good", "correct"]):
            reply = "😊 That is an excellent answer! I am happy to hear that. 👍"
        elif any(kw in text_lower for kw in ["explain", "clarify", "unsure", "what"]):
            reply = "🤔 Could you explain that again? I want to make sure I understand. ❓"
        elif any(kw in text_lower for kw in ["unfortunately", "fail", "failed", "sorry", "incorrect"]):
            reply = "🙁 That's unfortunate. Let's move on to the next question. 😢"
        else:
            reply = "🙂 Thank you. Let's explore your frontend experience in PySide and QPainter. 🤔"

        QTimer.singleShot(1500, lambda: self._start_streaming_response(reply))

    def _tick_timer(self):
        self._elapsed += 1
        h = self._elapsed // 3600
        m = (self._elapsed % 3600) // 60
        s = self._elapsed % 60
        self._timer_lbl.setText(f"{h:02}:{m:02}:{s:02}")

    # ─────────────────────────────────────────────────────────
    # Screen lifecycle
    # ─────────────────────────────────────────────────────────

    def on_enter(self):
        super().on_enter()
        resolver = self.ctx.theme_manager._engine.resolver
        self._elapsed = 0
        self._run_timer.start(1000)
        self._status_badge.set_level(BadgeLevel.BUSY)
        self._session_id_lbl.setText(
            "SESSION: 0x" + __import__("uuid").uuid4().hex[:8].upper()
        )

        if hasattr(self._transcript, 'clear'):
            self._transcript.clear()

        # Reset and initialize MascotController
        self._mascot.controller.initialize()

        if hasattr(self._transcript, 'append_line'):
            self._transcript.append_line(
                "TellMe Interview Session — Initialized",
                resolver.resolve_color("colors.accent")
            )
            self._transcript.append_line(
                "─" * 60 + "\n",
                resolver.resolve_color("colors.border")
            )

        # Trigger dynamic streaming greeting
        QTimer.singleShot(600, lambda: self._start_streaming_response(
            "Hello! 😊 I will be your interviewer today. Let's start with a brief introduction. "
            "Tell me about yourself and your background. 🤔"
        ))

    def on_leave(self):
        super().on_leave()
        self._run_timer.stop()
        self._waveform.set_active(False)
        self._mascot.controller.shutdown()
