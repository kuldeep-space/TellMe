"""
Settings Screen — .conf / .toml style configuration file interface.
Organized by sections with CoreToggle, CoreInput, TerminalCombo.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QSplitter, QScrollArea, QStackedWidget
)
from PySide6.QtCore import Qt
from frontend.core.base_screen import BaseScreen
from frontend.core.app_context import AppContext
from frontend.themes.base_theme import LabelRole
from .viewmodel import SettingsViewModel


class SettingsScreen(BaseScreen):
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(ctx, parent)
        self.vm = SettingsViewModel(ctx, self)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        self._engine = self.ctx.theme_manager._engine
        self._resolver = self._engine.resolver if self._engine else None

        bg_trans = "background: transparent;"
        if self._resolver:
            c_primary = self._resolver.resolve_color("colors.accent")
            c_border = self._resolver.resolve_color("colors.border")
            c_muted = self._resolver.resolve_color("colors.text_muted")
            c_text = self._resolver.resolve_color("colors.text_primary")
            c_hover = self._resolver.resolve_color("colors.surface_hover")
        else:
            c_primary = "#ff6600"
            c_border = "#0f1114"
            c_muted = "#6a7178"
            c_text = "#e6e6e6"
            c_hover = "#2d3339"

        hdr = QLabel("$ tellme config --edit")
        hdr.setStyleSheet(f"color: {c_primary}; font-size: 14px; {bg_trans}")
        root.addWidget(hdr)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: " + c_border + "; }")

        # Left: section nav
        sections = ["[appearance]", "[audio]", "[inference]", "[paths]", "[logging]", "[about]"]
        self._section_list = QListWidget()
        self._section_list.setFixedWidth(180)
        self._section_list.setStyleSheet(
            "QListWidget { background: transparent; border: none; border-right: 1px solid " + c_border + "; }"
            "QListWidget::item { padding: 8px 12px; color: " + c_muted + "; font-size: 11px; }"
            "QListWidget::item:selected { color: " + c_text + "; border-left: 2px solid " + c_primary + "; background: " + c_hover + "; }"
        )
        for sec in sections:
            self._section_list.addItem(QListWidgetItem(sec))
        self._section_list.setCurrentRow(0)
        self._section_list.currentRowChanged.connect(self._switch_section)
        splitter.addWidget(self._section_list)

        # Right: content stack
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_appearance())
        self._stack.addWidget(self._build_audio())
        self._stack.addWidget(self._build_inference())
        self._stack.addWidget(self._build_paths())
        self._stack.addWidget(self._build_logging())
        self._stack.addWidget(self._build_about())
        splitter.addWidget(self._stack)
        splitter.setSizes([180, 820])

        root.addWidget(splitter, stretch=1)

    def _switch_section(self, idx: int):
        self._stack.setCurrentIndex(idx)

    # ── Section builders ──────────────────────────────────────────────
    def _section_scroll(self, win: QWidget) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setWidget(win)
        return scroll

    def _setting_row(self, parent_layout, key: str, widget: QWidget, desc: str = ""):
        c_primary = self._resolver.resolve_color("colors.accent") if self._resolver else "#ff6600"
        
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 2, 0, 2)
        hl.setSpacing(16)
        kl = QLabel(key)
        kl.setStyleSheet(
            f"color: {c_primary}; font-size: 11px; "
            f"background: transparent; min-width: 200px;"
        )
        hl.addWidget(kl)
        hl.addWidget(widget)
        if desc:
            hl.addWidget(self.ctx.ui.make_label(desc, role=LabelRole.MUTED.value))
        hl.addStretch()
        parent_layout.addWidget(row)

    def _build_appearance(self) -> QWidget:
        win = self.ctx.ui.make_window("[appearance]")
        
        # Theme Selection
        theme_widget = QWidget()
        theme_layout = QHBoxLayout(theme_widget)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setSpacing(8)
        
        btn_terminal = self.ctx.ui.make_button("TERMINAL")
        btn_terminal.clicked.connect(lambda: self.ctx.theme_manager.apply_theme("terminal"))
        
        btn_industrial = self.ctx.ui.make_button("INDUSTRIAL")
        btn_industrial.clicked.connect(lambda: self.ctx.theme_manager.apply_theme("industrial"))
        
        theme_layout.addWidget(btn_terminal)
        theme_layout.addWidget(btn_industrial)
        theme_layout.addStretch()
        
        self._setting_row(win.body_layout, "active_theme",     theme_widget, "Select UI Theme")
        self._setting_row(win.body_layout, "crt_scanlines",    self.ctx.ui.make_toggle(True),  "Enable CRT scanline effect")
        self._setting_row(win.body_layout, "crt_vignette",     self.ctx.ui.make_toggle(True),  "Enable edge vignette")
        self._setting_row(win.body_layout, "crt_flicker",      self.ctx.ui.make_toggle(False), "Enable subtle phosphor flicker")
        self._setting_row(win.body_layout, "sidebar_width",    self.ctx.ui.make_input("220", "= "), "Sidebar width in pixels")
        self._setting_row(win.body_layout, "font_size",        self.ctx.ui.make_input("12", "= "),  "Base font size (px)")
        win.add_stretch()
        return self._section_scroll(win)

    def _build_audio(self) -> QWidget:
        win = self.ctx.ui.make_window("[audio]")
        self._setting_row(win.body_layout, "mic_enabled",      self.ctx.ui.make_toggle(True),  "Enable microphone input")
        self._setting_row(win.body_layout, "mic_device",       self.ctx.ui.make_input("default", "= "), "Audio device name or index")
        self._setting_row(win.body_layout, "sample_rate",      self.ctx.ui.make_input("16000", "= "), "Sample rate (Hz)")
        self._setting_row(win.body_layout, "vad_threshold",    self.ctx.ui.make_input("0.5", "= "),   "Voice activity detection threshold")
        win.add_stretch()
        return self._section_scroll(win)

    def _build_inference(self) -> QWidget:
        win = self.ctx.ui.make_window("[inference]")
        self._setting_row(win.body_layout, "backend",          self.ctx.ui.make_input("llama.cpp", "= "), "Inference backend")
        self._setting_row(win.body_layout, "default_model",    self.ctx.ui.make_input("auto", "= "),  "Default model path or 'auto'")
        self._setting_row(win.body_layout, "n_ctx",            self.ctx.ui.make_input("4096", "= "),  "Context window size (tokens)")
        self._setting_row(win.body_layout, "n_threads",        self.ctx.ui.make_input("8", "= "),     "CPU threads to use")
        self._setting_row(win.body_layout, "temperature",      self.ctx.ui.make_input("0.7", "= "),   "Sampling temperature")
        self._setting_row(win.body_layout, "top_p",            self.ctx.ui.make_input("0.95", "= "),  "Top-p (nucleus) sampling")
        self._setting_row(win.body_layout, "gpu_layers",       self.ctx.ui.make_input("0", "= "),     "GPU offload layers (0 = CPU only)")
        win.add_stretch()
        return self._section_scroll(win)

    def _build_paths(self) -> QWidget:
        win = self.ctx.ui.make_window("[paths]")
        self._setting_row(win.body_layout, "models_dir",  self.ctx.ui.make_input("models/", "= "),   "Model files directory")
        self._setting_row(win.body_layout, "sessions_dir",self.ctx.ui.make_input("runtime/sessions/", "= "), "Session storage directory")
        self._setting_row(win.body_layout, "logs_dir",    self.ctx.ui.make_input("runtime/logs/", "= "),     "Log files directory")
        self._setting_row(win.body_layout, "reports_dir", self.ctx.ui.make_input("runtime/reports/", "= "),  "Reports directory")
        win.add_stretch()
        return self._section_scroll(win)

    def _build_logging(self) -> QWidget:
        win = self.ctx.ui.make_window("[logging]")
        self._setting_row(win.body_layout, "log_level",   self.ctx.ui.make_input("INFO", "= "),      "Log level (DEBUG/INFO/WARN/ERROR)")
        self._setting_row(win.body_layout, "log_to_file", self.ctx.ui.make_toggle(True),              "Write logs to file")
        self._setting_row(win.body_layout, "max_log_size",self.ctx.ui.make_input("10", "= "),         "Max log file size (MB)")
        self._setting_row(win.body_layout, "max_backups", self.ctx.ui.make_input("5", "= "),          "Max log backup files")
        win.add_stretch()
        return self._section_scroll(win)

    def _build_about(self) -> QWidget:
        win = self.ctx.ui.make_window("[about]")
        c_primary = self._resolver.resolve_color("colors.accent") if self._resolver else "#ff6600"
        c_text = self._resolver.resolve_color("colors.text_primary") if self._resolver else "#e6e6e6"
        for line in [
            ("application",  "TellMe"),
            ("version",      "0.1.0-alpha"),
            ("build",        "2026-07-18"),
            ("framework",    "PySide6 6.11.1"),
            ("python",       "3.12.0"),
            ("architecture", "MVVM + backend services"),
            ("license",      "MIT"),
        ]:
            k, v = line
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            hl = QHBoxLayout(row)
            hl.setContentsMargins(0, 2, 0, 2)
            kl = QLabel(k)
            kl.setStyleSheet(f"color: {c_primary}; font-size: 11px; background: transparent; min-width: 160px;")
            vl = QLabel(f"= {v}")
            vl.setStyleSheet(f"color: {c_text}; font-size: 11px; background: transparent;")
            hl.addWidget(kl)
            hl.addWidget(vl)
            hl.addStretch()
            win.body_layout.addWidget(row)
        win.add_stretch()
        return self._section_scroll(win)
