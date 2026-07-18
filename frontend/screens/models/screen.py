"""
Models Screen — Package Manager style model management.
Resembles pip/apt/docker output.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QSplitter
)
from PySide6.QtCore import Qt
from frontend.core.base_screen import BaseScreen
from frontend.core.app_context import AppContext
from frontend.themes.base_theme import ButtonVariant
from .viewmodel import ModelsViewModel

_MODELS = [
    {"name": "llama3-8b-q4_k_m.gguf", "arch": "LLaMA-3", "quant": "Q4_K_M", "ctx": 8192,  "ram": "5.2 GB", "backend": "llama.cpp", "status": "ready"},
    {"name": "mistral-7b-v0.3.q4.gguf","arch": "Mistral",  "quant": "Q4_0",   "ctx": 4096,  "ram": "4.1 GB", "backend": "llama.cpp", "status": "offline"},
    {"name": "phi3-mini-q8.gguf",       "arch": "Phi-3",    "quant": "Q8_0",   "ctx": 2048,  "ram": "2.8 GB", "backend": "llama.cpp", "status": "offline"},
]


class ModelsScreen(BaseScreen):
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(ctx, parent)
        self.vm = ModelsViewModel(ctx, self)
        self._selected_model = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        hdr = self.ctx.ui.make_label("$ tellme model list", role="primary")
        root.addWidget(hdr)

        self._engine = self.ctx.theme_manager._engine
        self._resolver = self._engine.resolver if self._engine else None
        c_border = self._resolver.resolve_color("colors.border") if self._resolver else "#1f521f"

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {c_border}; }}"
        )

        # Left: model list
        list_win = self.ctx.ui.make_window("INSTALLED MODELS")
        self._list = QListWidget()
        self._list.setStyleSheet(
            "QListWidget { background: transparent; border: none; }"
            "QListWidget::item { padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }"
        )
        for m in _MODELS:
            badge = "[ READY  ]" if m["status"] == "ready" else "[ OFFLINE]"
            text  = f"  {badge}  {m['name']}"
            item  = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, m)
            self._list.addItem(item)

        self._list.currentItemChanged.connect(self._on_select)
        list_win.add_widget(self._list)

        add_row = QHBoxLayout()
        self._add_input = self.ctx.ui.make_input(placeholder="Path to .gguf file...", prompt="Path")
        self._add_btn   = self.ctx.ui.make_button("ADD MODEL")
        self._add_btn.clicked.connect(self._add_model)
        add_row.addWidget(self._add_input, stretch=1)
        add_row.addWidget(self._add_btn)
        list_win.add_layout(add_row)
        splitter.addWidget(list_win)

        # Right: detail
        self._detail = self.ctx.ui.make_window("MODEL DETAILS")
        self._detail.add_widget(self.ctx.ui.make_label("  Select a model to view details.", role="muted"))
        self._detail_content = QWidget()
        self._detail_content.setStyleSheet("background: transparent;")
        self._detail_content.setVisible(False)
        dc = QVBoxLayout(self._detail_content)
        dc.setContentsMargins(0, 0, 0, 0)
        dc.setSpacing(4)

        self._df: dict[str, QLabel] = {}
        for k in ["NAME", "ARCH", "QUANTIZATION", "CONTEXT", "RAM ESTIMATE", "BACKEND", "STATUS"]:
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            hl = QHBoxLayout(row)
            hl.setContentsMargins(0, 0, 0, 0)
            kl = self.ctx.ui.make_label(f"{k:<14}", role="muted")
            vl = self.ctx.ui.make_label("—")
            hl.addWidget(kl)
            hl.addWidget(vl, stretch=1)
            dc.addWidget(row)
            self._df[k] = vl

        dc.addWidget(self.ctx.ui.make_separator())

        btn_row = QHBoxLayout()
        self._load_btn   = self.ctx.ui.make_button("LOAD")
        self._verify_btn = self.ctx.ui.make_button("VERIFY")
        self._remove_btn = self.ctx.ui.make_button("REMOVE", variant=ButtonVariant.DANGER)
        btn_row.addWidget(self._load_btn)
        btn_row.addWidget(self._verify_btn)
        btn_row.addWidget(self._remove_btn)
        btn_row.addStretch()
        dc.addLayout(btn_row)
        dc.addStretch()

        self._detail.add_widget(self._detail_content)
        splitter.addWidget(self._detail)
        splitter.setSizes([400, 600])
        root.addWidget(splitter, stretch=1)

    def _on_select(self, current, _):
        if not current:
            return
        m = current.data(Qt.ItemDataRole.UserRole)
        self._detail_content.setVisible(True)
        self._df["NAME"].setText(m["name"])
        self._df["ARCH"].setText(m["arch"])
        self._df["QUANTIZATION"].setText(m["quant"])
        self._df["CONTEXT"].setText(f"{m['ctx']} tokens")
        self._df["RAM ESTIMATE"].setText(m["ram"])
        self._df["BACKEND"].setText(m["backend"])
        self._df["STATUS"].setText(m["status"].upper())

    def _add_model(self):
        path = self._add_input.text().strip()
        if path:
            self._add_input.clear()
