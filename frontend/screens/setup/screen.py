"""
Setup Screen — CLI-style interview configuration.
Feels like running: $ tellme interview create [flags]
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QScrollArea, QSlider, QSpinBox
)
from PySide6.QtCore import Qt, Signal

from frontend.core.base_screen import BaseScreen
from frontend.core.app_context import AppContext
from frontend.themes.base_theme import ButtonVariant
from .viewmodel import SetupViewModel


class SetupScreen(BaseScreen):
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(ctx, parent)
        self.vm = SetupViewModel(ctx, self)
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

        # ── Header ────────────────────────────────────────────────────
        hdr = self.ctx.ui.make_label("$ tellme interview create", role="primary")
        main.addWidget(hdr)
        sub = self.ctx.ui.make_label("Configure all flags before executing the interview session.", role="muted")
        main.addWidget(sub)
        main.addWidget(self.ctx.ui.make_separator())

        # ── Flag form ─────────────────────────────────────────────────
        form_win = self.ctx.ui.make_window("CONFIGURATION FLAGS")

        # --type
        form_win.add_widget(self._flag_label("--type", "Interview type"))
        self._type_combo = _TerminalCombo(["Behavioral", "Technical", "System Design", "HR"])
        form_win.add_widget(self._type_combo)

        form_win.add_widget(self.ctx.ui.make_separator())

        # --difficulty
        form_win.add_widget(self._flag_label("--difficulty", "Difficulty level"))
        self._diff_combo = _TerminalCombo(["easy", "medium", "hard", "expert"])
        self._diff_combo.set_index(1)
        form_win.add_widget(self._diff_combo)

        form_win.add_widget(self.ctx.ui.make_separator())

        # --language
        form_win.add_widget(self._flag_label("--language", "Language"))
        self._lang_combo = _TerminalCombo(["English", "Hindi", "Spanish", "French", "German"])
        form_win.add_widget(self._lang_combo)

        form_win.add_widget(self.ctx.ui.make_separator())

        # --duration
        form_win.add_widget(self._flag_label("--duration", "Duration (minutes)"))
        self._dur_spin = QSpinBox()
        self._dur_spin.setRange(5, 90)
        self._dur_spin.setValue(30)
        self._dur_spin.setSuffix(" min")
        self._dur_spin.setFixedWidth(100)
        form_win.add_widget(self._dur_spin)

        form_win.add_widget(self.ctx.ui.make_separator())

        # --role
        form_win.add_widget(self._flag_label("--role", "Target role"))
        self._role_input = self.ctx.ui.make_input(placeholder="Software Engineer", prompt="--role ")
        form_win.add_widget(self._role_input)

        form_win.add_widget(self.ctx.ui.make_separator())

        # --company
        form_win.add_widget(self._flag_label("--company", "Target company (optional)"))
        self._company_input = self.ctx.ui.make_input(placeholder="Google, Meta, etc.", prompt="--company ")
        form_win.add_widget(self._company_input)

        form_win.add_widget(self.ctx.ui.make_separator())

        # --resume
        form_win.add_widget(self._flag_label("--resume", "Resume / CV path"))
        resume_row = QHBoxLayout()
        self._resume_input = self.ctx.ui.make_input(placeholder="Drag PDF here or type path...", prompt="--resume ")
        self._resume_btn   = self.ctx.ui.make_button("BROWSE")
        self._resume_btn.clicked.connect(self._browse_resume)
        resume_row.addWidget(self._resume_input, stretch=1)
        resume_row.addWidget(self._resume_btn)
        form_win.add_layout(resume_row)

        form_win.add_widget(self.ctx.ui.make_separator())

        # --jd
        form_win.add_widget(self._flag_label("--jd", "Job description path (optional)"))
        jd_row = QHBoxLayout()
        self._jd_input = self.ctx.ui.make_input(placeholder="Path to job description PDF or text...", prompt="--jd ")
        self._jd_btn   = self.ctx.ui.make_button("BROWSE")
        self._jd_btn.clicked.connect(self._browse_jd)
        jd_row.addWidget(self._jd_input, stretch=1)
        jd_row.addWidget(self._jd_btn)
        form_win.add_layout(jd_row)

        main.addWidget(form_win)

        # ── Advanced Settings ─────────────────────────────────────────
        adv_win = self.ctx.ui.make_window("ADVANCED FLAGS")

        adv_win.add_widget(self._flag_label("--model", "Language model"))
        self._model_combo = _TerminalCombo(["auto-select", "llama3-8b-q4", "mistral-7b-q4"])
        adv_win.add_widget(self._model_combo)

        adv_win.add_widget(self.ctx.ui.make_separator())

        adv_win.add_widget(self._flag_label("--temperature", "Temperature"))
        self._temp_input = self.ctx.ui.make_input(placeholder="0.7", prompt="--temperature ")
        adv_win.add_widget(self._temp_input)

        adv_win.add_widget(self.ctx.ui.make_separator())

        adv_win.add_widget(self._flag_label("--ctx-len", "Context length (tokens)"))
        self._ctx_combo = _TerminalCombo(["1024", "2048", "4096", "8192"])
        self._ctx_combo.set_index(2)
        adv_win.add_widget(self._ctx_combo)

        main.addWidget(adv_win)

        # ── Execute bar ───────────────────────────────────────────────
        exec_win = self.ctx.ui.make_window("EXECUTE", accent=True)
        exec_row = QHBoxLayout()

        self._preview_lbl = self.ctx.ui.make_label(self._build_preview(), role="muted")

        btn_exec = self.ctx.ui.make_button("INITIALIZE INTERVIEW")
        btn_exec.clicked.connect(self._execute)
        btn_back = self.ctx.ui.make_button("ABORT", variant=ButtonVariant.DANGER)
        btn_back.clicked.connect(self.vm.go_back)

        exec_row.addWidget(self._preview_lbl, stretch=1)
        exec_row.addWidget(btn_exec)
        exec_row.addWidget(btn_back)
        exec_win.add_layout(exec_row)
        main.addWidget(exec_win)

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ── Helpers ───────────────────────────────────────────────────────
    def _flag_label(self, flag: str, desc: str) -> QWidget:
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 2, 0, 2)
        hl.setSpacing(12)
        
        f = self.ctx.ui.make_label(flag, role="primary")
        f.setMinimumWidth(120)
        
        d = self.ctx.ui.make_label(desc, role="muted")
        hl.addWidget(f)
        hl.addWidget(d)
        hl.addStretch()
        return row

    def _build_preview(self) -> str:
        return "$ tellme interview create [flags] ..."

    def _browse_resume(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Select Resume", "", "PDF Files (*.pdf)")
        if path:
            self._resume_input.set_text(path)
            self.vm.resume_path = path

    def _browse_jd(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Select Job Description", "", "PDF Files (*.pdf);;Text Files (*.txt)")
        if path:
            self._jd_input.set_text(path)

    def _execute(self):
        self.vm.interview_type = self._type_combo.current_value()
        self.vm.company        = self._company_input.text()
        self.vm.begin_interview()


class _TerminalCombo(QWidget):
    """A QComboBox styled for the terminal."""
    def __init__(self, options: list, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(self)
        hl.setContentsMargins(0, 0, 0, 0)
        self._combo = QComboBox()
        self._combo.setObjectName("terminalCombo")
        self._combo.addItems(options)
        hl.addWidget(self._combo)
        hl.addStretch()

    def current_value(self) -> str:
        return self._combo.currentText()

    def set_index(self, idx: int):
        self._combo.setCurrentIndex(idx)
