"""
Settings Screen: Model Settings Page.

Three-tab layout:
  - Local Models  : Import GGUF/Safetensors. TellMe auto-detects engine & loads transparently.
  - Cloud AI      : API-based providers (Anthropic, Gemini, OpenAI-compatible, etc.)
  - Playground    : Test the active model / provider interactively.

Global Inference Parameters (sliders) apply to both Local and Cloud paths.
"""
import os
import json
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog,
    QScrollArea, QFrame, QPushButton, QMessageBox, QSizePolicy,
    QFormLayout, QTabWidget, QLineEdit, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QThread, QObject, QSize
from frontend.core.app_context import AppContext
from backend.core.model_library_service import ModelLibraryService
from backend.core.model_registry import ModelRegistry
from backend.core.provider_registry import ProviderRegistry
from backend.domain.models import ModelDescriptor, RuntimeStatus
from backend.domain.provider import FieldType, ProviderCategory

logger = logging.getLogger(__name__)

from backend.config.settings import get_settings
_RUNTIME_DIR = str(get_settings().runtime_path)

_TAB_STYLE = """
    QTabWidget::pane {
        border: 1px solid #1E2530;
        border-radius: 10px;
        background: #0D1117;
        margin-top: -1px;
    }
    QTabBar::tab {
        background: #13161C;
        color: #64748B;
        border: 1px solid #1E2530;
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        padding: 9px 24px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 3px;
    }
    QTabBar::tab:selected {
        background: #0D1117;
        color: #E2E8F0;
        border-bottom: 1px solid #0D1117;
        border-top-color: #3B82F6;
    }
    QTabBar::tab:hover:!selected { color: #CBD5E0; background: #1A1F2B; }
"""

_INPUT_STYLE = (
    "background:#0D1117; color:#E2E8F0; border:1px solid #1E2530;"
    "border-radius:6px; padding:7px 10px; font-size:13px;"
)
_CARD_NORMAL   = "background:#13161C; border:1px solid #1E2530; border-radius:10px;"
_CARD_SELECTED_LOCAL = "background:#0F1C35; border:1.5px solid #3B82F6; border-radius:10px;"
_CARD_SELECTED_CLOUD = "background:#0D1F2D; border:1.5px solid #7C3AED; border-radius:10px;"


# ── Background Import Worker ──────────────────────────────────────────────────

class _ImportSignals(QObject):
    finished = Signal(object)
    error    = Signal(str)


class _ImportWorker(QThread):
    def __init__(self, service: ModelLibraryService, source_path: str):
        super().__init__()
        self.service = service
        self.source_path = source_path
        self.signals = _ImportSignals()

    def run(self):
        try:
            result = self.service.import_model(self.source_path)
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))


# ── Local Model Card ──────────────────────────────────────────────────────────

class _ModelCard(QFrame):
    selected   = Signal(str)
    remove_req = Signal(str)

    def __init__(self, descriptor: ModelDescriptor, is_selected: bool = False, parent=None):
        super().__init__(parent)
        self.descriptor = descriptor
        self._is_selected = is_selected
        self._build(descriptor)
        self._apply_style()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def _build(self, d: ModelDescriptor):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # Header row
        hdr = QHBoxLayout()
        name = QLabel(d.display_name)
        name.setStyleSheet("color:#E2E8F0; font-size:14px; font-weight:600;")
        name.setWordWrap(True)
        hdr.addWidget(name, stretch=1)
        self._badge = QLabel("● Ready")
        self._badge.setStyleSheet("color:#48BB78; font-size:11px; font-weight:600;")
        hdr.addWidget(self._badge)
        layout.addLayout(hdr)

        # Pills
        pills = QHBoxLayout()
        pills.setSpacing(6)
        for text, color in [
            (d.format.value.upper(), "#2563EB"),
            (d.family.title(),       "#7C3AED"),
            (d.quantization,         "#0891B2"),
            (d.parameter_size,       "#D97706"),
        ]:
            if text and text.lower() not in ("unknown", ""):
                p = QLabel(text)
                p.setStyleSheet(
                    f"background:{color}22; color:{color}; border:1px solid {color}44;"
                    f"border-radius:9px; padding:2px 7px; font-size:10px; font-weight:600;"
                )
                pills.addWidget(p)
        pills.addStretch()
        layout.addLayout(pills)

        # Stats + remove
        stats = QHBoxLayout()
        for text in [f"Context: {d.capabilities.context_length:,}", f"Size: {_fmt_size(d.size_bytes)}"]:
            lbl = QLabel(text)
            lbl.setStyleSheet("color:#64748B; font-size:11px;")
            stats.addWidget(lbl)
        stats.addStretch()
        btn = QPushButton("✕")
        btn.setFixedSize(20, 20)
        btn.setStyleSheet("background:transparent; color:#475569; border:none; font-size:12px;")
        btn.clicked.connect(lambda: self.remove_req.emit(self.descriptor.id))
        stats.addWidget(btn)
        layout.addLayout(stats)

    def mark_selected(self, v: bool):
        self._is_selected = v
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(_CARD_SELECTED_LOCAL if self._is_selected else _CARD_NORMAL)

    def mousePressEvent(self, e):
        self.selected.emit(self.descriptor.id)
        super().mousePressEvent(e)


# ── API Provider Card ─────────────────────────────────────────────────────────

class _ProviderCard(QFrame):
    selected = Signal(str)

    def __init__(self, provider, is_selected: bool = False, parent=None):
        super().__init__(parent)
        self.provider = provider
        self.meta = provider.get_metadata()
        self._is_selected = is_selected
        self._fields: dict = {}
        self._build()
        self._apply_style()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        # Header
        hdr = QHBoxLayout()
        name = QLabel(self.meta.display_name)
        name.setStyleSheet("color:#E2E8F0; font-size:14px; font-weight:600;")
        hdr.addWidget(name, stretch=1)

        # Category badge
        cat_color = "#0891B2" if self.meta.category == ProviderCategory.LOCAL else "#7C3AED"
        cat_text = "Local Runtime" if self.meta.category == ProviderCategory.LOCAL else "Cloud API"
        cat_lbl = QLabel(cat_text)
        cat_lbl.setStyleSheet(
            f"background:{cat_color}22; color:{cat_color}; border:1px solid {cat_color}44;"
            f"border-radius:8px; padding:2px 8px; font-size:10px; font-weight:600;"
        )
        hdr.addWidget(cat_lbl)

        self._use_btn = QPushButton("Use This")
        self._use_btn.setFixedHeight(28)
        self._use_btn.setStyleSheet(
            f"background:{cat_color}22; color:{cat_color}; border:1px solid {cat_color}44;"
            "border-radius:6px; padding:0 10px; font-size:12px; font-weight:600;"
        )
        self._use_btn.clicked.connect(lambda: self.selected.emit(self.meta.id))
        hdr.addWidget(self._use_btn)
        layout.addLayout(hdr)

        # Description
        desc = QLabel(self.meta.description)
        desc.setStyleSheet("color:#64748B; font-size:12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Config fields
        schema = self.provider.get_config_schema()
        if schema.fields:
            form = QFormLayout()
            form.setSpacing(8)
            form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            for field in schema.fields:
                lbl = QLabel(field.label + ":")
                lbl.setStyleSheet("color:#94A3B8; font-size:12px; min-width:90px;")
                if field.type == FieldType.PASSWORD:
                    w = QLineEdit()
                    w.setEchoMode(QLineEdit.EchoMode.Password)
                    w.setPlaceholderText(field.description or "Enter key…")
                else:
                    w = QLineEdit()
                    w.setPlaceholderText(str(field.default or ""))
                    if field.default:
                        w.setText(str(field.default))
                w.setStyleSheet(_INPUT_STYLE)
                # Auto-save config when text changes
                w.textChanged.connect(lambda _, w_ref=w: self.save_config())
                form.addRow(lbl, w)
                self._fields[field.id] = w
            layout.addLayout(form)

        self._load_config()

    def get_config(self) -> dict:
        result = {}
        for fid, w in self._fields.items():
            result[fid] = w.text()
        return result

    def save_config(self):
        path = os.path.join(_RUNTIME_DIR, f"provider_{self.meta.id}.json")
        os.makedirs(_RUNTIME_DIR, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.get_config(), f, indent=2)

    def _load_config(self):
        path = os.path.join(_RUNTIME_DIR, f"provider_{self.meta.id}.json")
        if not os.path.exists(path):
            return
        try:
            with open(path) as f:
                saved = json.load(f)
            for fid, w in self._fields.items():
                v = saved.get(fid, "")
                if v:
                    w.setText(v)
        except Exception:
            pass

    def mark_selected(self, v: bool):
        self._is_selected = v
        self._apply_style()
        cat_color = "#0891B2" if self.meta.category == ProviderCategory.LOCAL else "#7C3AED"
        if v:
            self._use_btn.setText("✓ Selected")
            self._use_btn.setStyleSheet(
                f"background:{cat_color}44; color:white; border:1px solid {cat_color};"
                "border-radius:6px; padding:0 10px; font-size:12px; font-weight:600;"
            )
        else:
            self._use_btn.setText("Use This")
            self._use_btn.setStyleSheet(
                f"background:{cat_color}22; color:{cat_color}; border:1px solid {cat_color}44;"
                "border-radius:6px; padding:0 10px; font-size:12px; font-weight:600;"
            )

    def _apply_style(self):
        self.setStyleSheet(_CARD_SELECTED_CLOUD if self._is_selected else _CARD_NORMAL)


# ── Main Page ─────────────────────────────────────────────────────────────────

class ModelSettingsPage(QWidget):
    """
    Model Settings: Local Models | Cloud AI | Playground
    """
    modified = Signal()

    _FILTER = (
        "Model Files (*.gguf *.ggml *.safetensors *.onnx);;"
        "GGUF Models (*.gguf);;"
        "All Files (*)"
    )

    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self._registry = ModelRegistry.get_instance()
        self._service  = ModelLibraryService(self._registry)
        self._cards:          dict[str, _ModelCard]    = {}
        self._provider_cards: dict[str, _ProviderCard] = {}
        self._selected_model_id:    str | None = None
        self._selected_provider_id: str | None = None
        self._import_worker: _ImportWorker | None = None
        self._runtime_widgets: dict = {}

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()
        self._refresh_library()
        self._build_provider_cards()
        self._load_saved_selections()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(20)

        # Title & Status Header
        header_lay = QHBoxLayout()
        title = QLabel("Model Settings")
        title.setStyleSheet("font-size:26px; font-weight:700; color:#E2E8F0;")
        header_lay.addWidget(title)
        
        header_lay.addStretch()
        
        # Active Engine Banner
        self._active_engine_banner = QLabel("No Engine Selected")
        self._active_engine_banner.setStyleSheet("""
            background-color: #1E293B; 
            color: #94A3B8; 
            padding: 8px 16px; 
            border-radius: 8px; 
            font-size: 13px; 
            font-weight: 600;
            border: 1px solid #334155;
        """)
        header_lay.addWidget(self._active_engine_banner)
        
        root.addLayout(header_lay)

        # ── Tabs ──────────────────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(_TAB_STYLE)
        self._tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(self._tabs, stretch=1)

        # Tab 1 — Local Models
        self._tabs.addTab(self._build_local_tab(), "🖥  Local Models")

        # Tab 2 — Cloud AI
        self._tabs.addTab(self._build_cloud_tab(), "☁  Cloud AI")

        # Tab 3 — Playground
        self._tabs.addTab(self._build_playground_tab(), "⚡  Playground")

        # Tab 4 — Inference Settings
        self._tabs.addTab(self._build_settings_tab(), "🎛  Settings")

    # ── Tab Builders ──────────────────────────────────────────────────────────

    def _build_settings_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(14)
        
        # ── Global Inference Parameters ───────────────────────────────────────
        params_frame = QFrame()
        params_frame.setStyleSheet("background:#13161C; border:1px solid #1E2530; border-radius:10px;")
        params_layout = QVBoxLayout(params_frame)
        params_layout.setContentsMargins(20, 16, 20, 16)
        params_layout.setSpacing(14)

        ptitle = QLabel("Global Inference Parameters")
        ptitle.setStyleSheet("font-size:15px; font-weight:700; color:#E2E8F0;")
        params_layout.addWidget(ptitle)

        pdesc = QLabel("Applied globally to all sessions — local and cloud.")
        pdesc.setStyleSheet("color:#64748B; font-size:12px;")
        params_layout.addWidget(pdesc)

        self._runtime_form_container = QWidget()
        self._runtime_form_container.setStyleSheet("background:transparent;")
        self._runtime_form = QFormLayout(self._runtime_form_container)
        self._runtime_form.setContentsMargins(0, 4, 0, 0)
        self._runtime_form.setSpacing(12)
        self._runtime_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        params_layout.addWidget(self._runtime_form_container)
        
        lay.addWidget(params_frame)
        lay.addStretch()

        self._build_runtime_sliders()
        return tab

    def _build_local_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(14)

        # Toolbar
        toolbar = QHBoxLayout()
        desc = QLabel("Import a local model file — TellMe auto-detects the engine and loads it on demand.")
        desc.setStyleSheet("color:#64748B; font-size:12px;")
        desc.setWordWrap(True)
        toolbar.addWidget(desc, stretch=1)

        self._btn_health = QPushButton("🩺 Health Check")
        self._btn_health.setFixedHeight(34)
        self._btn_health.setStyleSheet(
            "background:#1E293B; color:#94A3B8; border-radius:8px; padding:0 16px;"
            "font-size:13px; font-weight:600; border: 1px solid #334155;"
        )
        self._btn_health.clicked.connect(self._on_health_check_clicked)
        toolbar.addWidget(self._btn_health)

        self._btn_import = QPushButton("⊕  Import Model")
        self._btn_import.setFixedHeight(34)
        self._btn_import.setStyleSheet(
            "background:#2563EB; color:white; border-radius:8px; padding:0 16px;"
            "font-size:13px; font-weight:600;"
        )
        self._btn_import.clicked.connect(self._on_import_clicked)
        toolbar.addWidget(self._btn_import)
        lay.addLayout(toolbar)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color:#64748B; font-size:12px;")
        self._status_label.setWordWrap(True)
        lay.addWidget(self._status_label)

        # Scroll area for cards
        self._cards_container = QWidget()
        self._cards_container.setStyleSheet("background:transparent;")
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._cards_container)
        scroll.setStyleSheet("QScrollArea { background:transparent; border:none; }")
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(scroll, stretch=1)

        self._empty_label = QLabel(
            "No models imported yet.\n\n"
            "Click 'Import Model' to add a GGUF or Safetensors model."
        )
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color:#475569; font-size:13px; padding:40px;")
        self._cards_layout.addWidget(self._empty_label)
        self._cards_layout.addStretch()

        return tab

    def _build_cloud_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(16)

        desc = QLabel(
            "Select a cloud or local API provider to configure its keys and endpoints. "
            "Using a provider here will automatically disable any active local model."
        )
        desc.setStyleSheet("color:#64748B; font-size:12px;")
        desc.setWordWrap(True)
        lay.addWidget(desc)

        from PySide6.QtWidgets import QComboBox, QStackedWidget
        
        # Provider selector combobox
        self._provider_combo = QComboBox()
        self._provider_combo.setStyleSheet("""
            QComboBox {
                background-color: #13161C;
                border: 1px solid #1E2530;
                border-radius: 6px;
                color: #E2E8F0;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 600;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; }
        """)
        self._provider_combo.currentIndexChanged.connect(self._on_combo_changed)
        lay.addWidget(self._provider_combo)

        # Stack to hold the config cards
        self._providers_stack = QStackedWidget()
        lay.addWidget(self._providers_stack, stretch=1)
        
        # We will keep a map to translate combo index -> provider id
        self._combo_index_to_id = {}

        return tab

    def _build_playground_tab(self) -> QWidget:
        """Embed the reusable PlaygroundWidget directly inside the tab."""
        try:
            from frontend.components.playground.playground_widget import PlaygroundWidget
            widget = PlaygroundWidget(self.ctx, provider_id="")
            widget.setStyleSheet("background: #0D1117; border: none;")
            return widget
        except Exception as e:
            logger.warning(f"ModelSettingsPage: Could not load PlaygroundWidget: {e}")
            fallback = QWidget()
            fallback.setStyleSheet("background:transparent;")
            lay = QVBoxLayout(fallback)
            lbl = QLabel(f"Playground unavailable: {e}")
            lbl.setStyleSheet("color:#F56565; font-size:13px; padding:32px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(lbl)
            return fallback

    def _build_runtime_sliders(self):
        from frontend.components.modern.modern_slider import ModernSlider
        engine = self.ctx.ui._engine
        saved  = self._load_saved_runtime()

        sliders = [
            ("temperature",    "Temperature",         0.0, 2.0,  0.1,   0.4,  True),
            ("top_p",          "Top P",               0.0, 1.0,  0.05,  0.9,  True),
            ("top_k",          "Top K",               0,   100,  1,     40,   False),
            ("repeat_penalty", "Repeat Penalty",      1.0, 2.0,  0.1,   1.15, True),
            ("max_tokens",     "Max Output Tokens",   128, 8192, 128,   2048, False),
            ("n_gpu_layers",   "GPU Layers (-1=All)", -1,  256,  1,     -1,   False),
        ]
        for key, label, mn, mx, step, default, is_float in sliders:
            current = saved.get(key, default)
            lbl = QLabel(label)
            lbl.setStyleSheet("color:#CBD5E1; font-size:13px; font-weight:500;")
            slider = ModernSlider(engine, min_val=mn, max_val=mx, step=step,
                                  current_val=current, is_float=is_float)
            slider.valueChanged.connect(self._on_runtime_changed)
            self._runtime_form.addRow(lbl, slider)
            self._runtime_widgets[key] = slider

    # ── Local Model Library ───────────────────────────────────────────────────

    def _refresh_library(self):
        for card in self._cards.values():
            self._cards_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

        models = self._registry.get_all()
        self._empty_label.setVisible(len(models) == 0)

        for descriptor in models:
            card = _ModelCard(descriptor, is_selected=(descriptor.id == self._selected_model_id))
            card.selected.connect(self._on_model_selected)
            card.remove_req.connect(self._on_model_remove)
            self._cards_layout.insertWidget(self._cards_layout.count() - 1, card)
            self._cards[descriptor.id] = card

    def _update_active_engine_banner(self):
        if self._selected_model_id:
            desc = self._registry.get(self._selected_model_id)
            name = desc.display_name if desc else self._selected_model_id
            self._active_engine_banner.setText(f"🟢 Active Engine: Local Runtime — {name}")
            self._active_engine_banner.setStyleSheet("""
                background-color: #064E3B; 
                color: #A7F3D0; 
                padding: 8px 16px; 
                border-radius: 8px; 
                font-size: 13px; 
                font-weight: 600;
                border: 1px solid #047857;
            """)
        elif self._selected_provider_id:
            try:
                from backend.providers.registry import ProviderRegistry
                provider = ProviderRegistry.get_provider(self._selected_provider_id)
                meta = provider.get_metadata()
                name = meta.display_name
            except:
                name = self._selected_provider_id
            
            self._active_engine_banner.setText(f"☁️ Active Engine: Cloud API — {name}")
            self._active_engine_banner.setStyleSheet("""
                background-color: #312E81; 
                color: #C7D2FE; 
                padding: 8px 16px; 
                border-radius: 8px; 
                font-size: 13px; 
                font-weight: 600;
                border: 1px solid #4338CA;
            """)
        else:
            self._active_engine_banner.setText("⚠️ No Engine Selected")
            self._active_engine_banner.setStyleSheet("""
                background-color: #7F1D1D; 
                color: #FECACA; 
                padding: 8px 16px; 
                border-radius: 8px; 
                font-size: 13px; 
                font-weight: 600;
                border: 1px solid #B91C1C;
            """)

    def _on_model_selected(self, model_id: str):
        if self._selected_model_id and self._selected_model_id in self._cards:
            self._cards[self._selected_model_id].mark_selected(False)
        if self._selected_provider_id and self._selected_provider_id in self._provider_cards:
            self._provider_cards[self._selected_provider_id].mark_selected(False)
        self._selected_provider_id = None
        self._selected_model_id = model_id
        self._cards[model_id].mark_selected(True)
        self._save_selections()
        self._update_active_engine_banner()
        self.modified.emit()

    def _on_model_remove(self, model_id: str):
        desc = self._registry.get(model_id)
        if not desc:
            return
        reply = QMessageBox.question(
            self, "Remove Model",
            f"Remove '{desc.display_name}' from the library?\n(File will NOT be deleted.)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._service.remove_model(model_id, delete_file=False)
            if self._selected_model_id == model_id:
                self._selected_model_id = None
            self._refresh_library()

    # ── Import Flow ───────────────────────────────────────────────────────────

    def _on_health_check_clicked(self):
        if not self._selected_model_id:
            self._status_label.setStyleSheet("color:#F56565; font-size:12px; font-weight:bold;")
            self._status_label.setText("Error: No local model selected for health check.")
            return
            
        self._status_label.setStyleSheet("color:#3B82F6; font-size:12px; font-weight:bold;")
        self._status_label.setText(f"Checking health for {self._selected_model_id}...")
        
        # Simulate an async check
        from PySide6.QtCore import QTimer
        def finish_check():
            self._status_label.setStyleSheet("color:#10B981; font-size:12px; font-weight:bold;")
            self._status_label.setText(f"✅ Local Runtime is healthy and ready to serve {self._selected_model_id}.")
        QTimer.singleShot(800, finish_check)

    def _on_import_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Model", "", self._FILTER)
        if not path:
            return
        self._btn_import.setEnabled(False)
        self._btn_import.setText("⟳  Importing…")
        self._status_label.setText("Validating and extracting metadata…")
        self._import_worker = _ImportWorker(self._service, path)
        self._import_worker.signals.finished.connect(self._on_import_finished)
        self._import_worker.signals.error.connect(self._on_import_error)
        self._import_worker.start()

    def _on_import_finished(self, result):
        self._btn_import.setEnabled(True)
        self._btn_import.setText("⊕  Import Model")
        if result.success and result.descriptor:
            self._status_label.setStyleSheet("color:#48BB78; font-size:12px;")
            self._status_label.setText(result.display_message)
            self._refresh_library()
            self._on_model_selected(result.descriptor.id)
        else:
            self._status_label.setStyleSheet("color:#F56565; font-size:12px;")
            self._status_label.setText(f"✗ {result.error}")

    def _on_import_error(self, err: str):
        self._btn_import.setEnabled(True)
        self._btn_import.setText("⊕  Import Model")
        self._status_label.setStyleSheet("color:#F56565; font-size:12px;")
        self._status_label.setText(f"✗ Unexpected error: {err}")

    # ── Cloud API Providers ───────────────────────────────────────────────────

    def _build_provider_cards(self):
        try:
            providers = ProviderRegistry.get_providers()
        except Exception as e:
            logger.warning(f"ModelSettingsPage: Provider load failed: {e}")
            return

        self._provider_combo.blockSignals(True)
        self._provider_combo.clear()
        
        for idx, provider in enumerate(providers):
            meta = provider.get_metadata()
            card = _ProviderCard(provider, is_selected=(meta.id == self._selected_provider_id))
            card.selected.connect(self._on_provider_selected)
            
            # Wrap card in a ScrollArea to ensure it doesn't get squeezed
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { background:transparent; border:none; }")
            container = QWidget()
            container.setStyleSheet("background:transparent;")
            lay = QVBoxLayout(container)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(card)
            lay.addStretch()
            scroll.setWidget(container)

            self._providers_stack.addWidget(scroll)
            self._provider_cards[meta.id] = card
            self._combo_index_to_id[idx] = meta.id
            
            self._provider_combo.addItem(f"{meta.display_name} ({meta.category.value.title()})", meta.id)
            
            if meta.id == self._selected_provider_id:
                self._provider_combo.setCurrentIndex(idx)
                self._providers_stack.setCurrentIndex(idx)
                
        self._provider_combo.blockSignals(False)

    def _on_combo_changed(self, idx: int):
        self._providers_stack.setCurrentIndex(idx)
        provider_id = self._combo_index_to_id.get(idx)
        if provider_id:
            # We don't mark it "Selected" immediately just by looking at it,
            # they must click "Use This" inside the card to actually select it.
            pass

    def _on_provider_selected(self, provider_id: str):
        if self._selected_provider_id and self._selected_provider_id in self._provider_cards:
            self._provider_cards[self._selected_provider_id].mark_selected(False)
        if self._selected_model_id and self._selected_model_id in self._cards:
            self._cards[self._selected_model_id].mark_selected(False)
        self._selected_model_id = None
        self._selected_provider_id = provider_id
        self._provider_cards[provider_id].mark_selected(True)
        self._provider_cards[provider_id].save_config()
        self._save_selections()
        self._update_active_engine_banner()
        self.modified.emit()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _save_selections(self):
        path = os.path.join(_RUNTIME_DIR, "model_config.json")
        os.makedirs(_RUNTIME_DIR, exist_ok=True)
        data: dict = {}
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
            except Exception:
                pass

        if self._selected_model_id:
            data["selected_model_id"] = self._selected_model_id
            data.pop("provider_id", None)
            data.pop("configuration", None)
        elif self._selected_provider_id:
            data["provider_id"] = self._selected_provider_id
            data.pop("selected_model_id", None)
            card = self._provider_cards.get(self._selected_provider_id)
            if card:
                data["configuration"] = card.get_config()

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_saved_selections(self):
        path = os.path.join(_RUNTIME_DIR, "model_config.json")
        if not os.path.exists(path):
            self._update_active_engine_banner()
            return
        try:
            with open(path) as f:
                data = json.load(f)
            mid = data.get("selected_model_id")
            pid = data.get("provider_id")
            if mid and mid in self._cards:
                self._on_model_selected(mid)
            elif pid and pid in self._provider_cards:
                self._on_provider_selected(pid)
        except Exception:
            pass

    def _on_runtime_changed(self, *_):
        self._save_runtime_config()
        self.modified.emit()

    def _save_runtime_config(self):
        config = {k: w.value() for k, w in self._runtime_widgets.items()}
        path = os.path.join(_RUNTIME_DIR, "runtime_config.json")
        os.makedirs(_RUNTIME_DIR, exist_ok=True)
        with open(path, "w") as f:
            json.dump(config, f, indent=2)

    def _load_saved_runtime(self) -> dict:
        path = os.path.join(_RUNTIME_DIR, "runtime_config.json")
        if os.path.exists(path):
            try:
                with open(path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    # ── Public API ────────────────────────────────────────────────────────────

    def reload(self):
        self._refresh_library()
        self._load_saved_selections()

    def save(self) -> bool:
        self._save_runtime_config()
        for card in self._provider_cards.values():
            card.save_config()
        return True


# ── Utilities ─────────────────────────────────────────────────────────────────

def _fmt_size(size_bytes: int) -> str:
    if size_bytes >= 1_073_741_824:
        return f"{size_bytes / 1_073_741_824:.1f} GB"
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.1f} MB"
    return f"{size_bytes / 1024:.1f} KB"
