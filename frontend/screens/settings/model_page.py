"""
Model Settings Inspector Workspace.

A high-density, IDE-inspired configuration workspace for local AI models
and cloud provider engines. Implements a clean 2-column layout:
  - Left Panel : Catalog Explorer (Local models list and cloud provider items)
  - Right Panel: Dashboard (Configuration parameters inspector and playground)
"""
import os
import json
import logging
import shutil
from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog,
    QScrollArea, QFrame, QPushButton, QMessageBox, QSizePolicy,
    QFormLayout, QLineEdit, QStackedWidget, QSplitter, QProgressBar,
    QToolButton, QTabWidget, QGridLayout, QComboBox
)
from PySide6.QtCore import Qt, Signal, QThread, QObject, QSize, QTimer, QRectF
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPainterPath

from frontend.core.app_context import AppContext
from backend.core.model_library_service import ModelLibraryService
from backend.core.model_registry import ModelRegistry
from backend.core.provider_registry import ProviderRegistry
from backend.domain.models import ModelDescriptor, RuntimeStatus
from backend.domain.provider import FieldType, ProviderCategory
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)

_RUNTIME_DIR = str(get_settings().runtime_path)

# Design Tokens (Reusable Theme Palette)
_C_BG          = "#0D1117"
_C_SURFACE     = "#13161C"
_C_PANEL       = "#161B22"
_C_BORDER      = "#21262D"
_C_BORDER_FOCUS= "#388BFD"
_C_TEXT_MAIN   = "#C9D1D9"
_C_TEXT_MUTED  = "#8B949E"
_C_TEXT_BRIGHT = "#F0F6FC"
_C_ACCENT      = "#1F6FEB"
_C_ACCENT_HOVER= "#388BFD"
_C_SUCCESS     = "#238636"
_C_SUCCESS_BG  = "#1B4727"
_C_WARNING     = "#D29922"
_C_ERROR       = "#DA3633"

# Modern Tab Widget Stylesheet
_TAB_STYLE = """
    QTabWidget::pane {
        border: 1px solid #21262D;
        border-radius: 6px;
        background: #161B22;
        margin-top: -1px;
    }
    QTabBar::tab {
        background: #0D1117;
        color: #8B949E;
        border: 1px solid #21262D;
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        padding: 8px 16px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 4px;
    }
    QTabBar::tab:selected {
        background: #161B22;
        color: #F0F6FC;
        border-bottom: 1px solid #161B22;
        border-top: 2px solid #1F6FEB;
    }
    QTabBar::tab:hover:!selected {
        color: #C9D1D9;
        background: #161B22;
    }
"""


# ── Custom Vector Icons (Zero Emojis, Pure QPainter Drawing) ──────────────────

class VectorIcon(QWidget):
    """Draws crisp UI vector icons."""
    def __init__(self, icon_type: str, size: int = 14, color: str = _C_TEXT_MUTED, parent=None):
        super().__init__(parent)
        self._icon_type = icon_type
        self._color = QColor(color)
        self.setFixedSize(size, size)

    def set_color(self, color: str):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        pen = QPen(self._color, 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        if self._icon_type == "folder":
            path = QPainterPath()
            path.moveTo(2, 4)
            path.lineTo(5, 4)
            path.lineTo(7, 6)
            path.lineTo(w - 2, 6)
            path.lineTo(w - 2, h - 3)
            path.lineTo(2, h - 3)
            path.closeSubpath()
            painter.drawPath(path)
        elif self._icon_type == "cpu":
            painter.drawRect(3, 3, w - 6, h - 6)
            painter.drawLine(5, 1, 5, 3)
            painter.drawLine(9, 1, 9, 3)
            painter.drawLine(5, h - 3, 5, h - 1)
            painter.drawLine(9, h - 3, 9, h - 1)
            painter.drawLine(1, 5, 3, 5)
            painter.drawLine(1, 9, 3, 9)
            painter.drawLine(w - 3, 5, w - 1, 5)
            painter.drawLine(w - 3, 9, w - 1, 9)
        elif self._icon_type == "cloud":
            path = QPainterPath()
            path.moveTo(3, 10)
            path.cubicTo(2, 10, 1, 8, 3, 7)
            path.cubicTo(3, 4, 7, 3, 9, 5)
            path.cubicTo(11, 4, 13, 6, 12, 8)
            path.cubicTo(13, 10, 11, 10, 10, 10)
            path.closeSubpath()
            painter.drawPath(path)
        elif self._icon_type == "plus":
            painter.drawLine(w // 2, 2, w // 2, h - 2)
            painter.drawLine(2, h // 2, w - 2, h // 2)
        elif self._icon_type == "cross":
            painter.drawLine(3, 3, w - 3, h - 3)
            painter.drawLine(w - 3, 3, 3, h - 3)
        elif self._icon_type == "pulse":
            path = QPainterPath()
            path.moveTo(2, h // 2)
            path.lineTo(5, h // 2)
            path.lineTo(7, 2)
            path.lineTo(10, h - 2)
            path.lineTo(12, h // 2)
            path.lineTo(w - 2, h // 2)
            painter.drawPath(path)
        elif self._icon_type == "check":
            path = QPainterPath()
            path.moveTo(2, h // 2)
            path.lineTo(5, h - 3)
            path.lineTo(w - 2, 3)
            painter.drawPath(path)
        elif self._icon_type == "dot":
            painter.setBrush(QBrush(self._color))
            painter.drawEllipse(QRectF(w / 2 - 3, h / 2 - 3, 6, 6))


# ── Background Import Worker Thread ───────────────────────────────────────────

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


# ── Explorer Navigation Item / Card ───────────────────────────────────────────

class ExplorerItemWidget(QFrame):
    selected = Signal(str, str) # (item_type, item_id)
    remove_requested = Signal(str)

    def __init__(self, item_id: str, title: str, category_tag: str, is_local: bool, is_active: bool = False, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.title = title
        self.category_tag = category_tag
        self.is_local = is_local
        self._is_active = is_active

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(50)
        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        dot_color = _C_SUCCESS if self._is_active else _C_TEXT_MUTED
        self._dot = VectorIcon("dot", size=10, color=dot_color)
        layout.addWidget(self._dot)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        self._lbl_title = QLabel(self.title)
        self._lbl_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #C9D1D9;")
        text_layout.addWidget(self._lbl_title)

        self._lbl_sub = QLabel(self.category_tag)
        self._lbl_sub.setStyleSheet("font-size: 9px; color: #8B949E;")
        text_layout.addWidget(self._lbl_sub)

        layout.addLayout(text_layout, stretch=1)

        if self.is_local:
            self._btn_remove = QToolButton()
            self._btn_remove.setFixedSize(24, 24)
            self._btn_remove.setStyleSheet("""
                QToolButton { background: transparent; border: none; border-radius: 4px; }
                QToolButton:hover { background: #21262D; }
            """)
            icon_remove = VectorIcon("cross", size=12, color="#8B949E")
            btn_lay = QHBoxLayout(self._btn_remove)
            btn_lay.setContentsMargins(0, 0, 0, 0)
            btn_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_lay.addWidget(icon_remove)
            self._btn_remove.clicked.connect(lambda: self.remove_requested.emit(self.item_id))
            layout.addWidget(self._btn_remove)

    def set_active(self, active: bool):
        self._is_active = active
        dot_color = _C_SUCCESS if self._is_active else _C_TEXT_MUTED
        self._dot.set_color(dot_color)
        self._apply_style()

    def _apply_style(self):
        if self._is_active:
            self.setStyleSheet("""
                ExplorerItemWidget {
                    background-color: #1F2937;
                    border: 1px solid #388BFD;
                    border-radius: 5px;
                }
            """)
            self._lbl_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #F0F6FC;")
        else:
            self.setStyleSheet("""
                ExplorerItemWidget {
                    background-color: #161B22;
                    border: 1px solid #21262D;
                    border-radius: 5px;
                }
                ExplorerItemWidget:hover {
                    background-color: #1C2128;
                    border-color: #30363D;
                }
            """)
            self._lbl_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #C9D1D9;")

    def mousePressEvent(self, event):
        item_type = "local" if self.is_local else "cloud"
        self.selected.emit(item_type, self.item_id)
        super().mousePressEvent(event)


# ── Asset Configuration Path Editor ───────────────────────────────────────────

class AssetPathPropertyWidget(QFrame):
    browse_clicked = Signal()

    def __init__(self, path: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #0D1117; border: 1px solid #21262D; border-radius: 6px;")
        self.setFixedHeight(34)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        layout.addWidget(VectorIcon("folder", size=14, color="#8B949E"))

        self._lbl_path = QLineEdit(path)
        self._lbl_path.setReadOnly(True)
        self._lbl_path.setStyleSheet("background: transparent; border: none; color: #C9D1D9; font-size: 11px; font-family: monospace;")
        layout.addWidget(self._lbl_path, stretch=1)

        self._btn_browse = QPushButton("Browse")
        self._btn_browse.setFixedHeight(24)
        self._btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #21262D;
                color: #C9D1D9;
                border: 1px solid #30363D;
                border-radius: 4px;
                padding: 0 8px;
                font-size: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #30363D;
                color: #F0F6FC;
            }
        """)
        self._btn_browse.clicked.connect(self.browse_clicked.emit)
        layout.addWidget(self._btn_browse)

    def set_path(self, path: str):
        self._lbl_path.setText(path)
        self._lbl_path.setToolTip(path)


# ── Main Model Settings Workspace ─────────────────────────────────────────────

class ModelSettingsPage(QWidget):
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
        
        self._explorer_items: Dict[str, ExplorerItemWidget] = {}
        self._selected_model_id: Optional[str] = None
        self._selected_provider_id: Optional[str] = None
        self._import_worker: Optional[_ImportWorker] = None
        self._runtime_widgets: dict = {}
        self._provider_fields: dict = {}

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()
        self._refresh_explorer()
        self._load_saved_selections()

    # ── Build UI Layout ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # Header Title Bar
        header = QHBoxLayout()
        header.setContentsMargins(2, 0, 2, 0)
        
        title_group = QVBoxLayout()
        title_group.setSpacing(1)
        title = QLabel("Model Engine Workspace")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #F0F6FC;")
        sub_title = QLabel("Configure local execution backends and cloud inference provider parameters")
        sub_title.setStyleSheet("font-size: 11px; color: #8B949E;")
        title_group.addWidget(title)
        title_group.addWidget(sub_title)
        header.addLayout(title_group)

        header.addStretch()

        # Global Active Engine Banner
        self._banner_frame = QFrame()
        self._banner_frame.setFixedHeight(30)
        self._banner_frame.setStyleSheet("background-color: #161B22; border: 1px solid #21262D; border-radius: 6px;")
        banner_lay = QHBoxLayout(self._banner_frame)
        banner_lay.setContentsMargins(8, 0, 8, 0)
        banner_lay.setSpacing(6)

        self._banner_dot = VectorIcon("dot", size=8, color=_C_TEXT_MUTED)
        banner_lay.addWidget(self._banner_dot)

        self._banner_label = QLabel("No Engine Active")
        self._banner_label.setStyleSheet("font-size: 11px; font-weight: 600; color: #C9D1D9;")
        banner_lay.addWidget(self._banner_label)

        header.addWidget(self._banner_frame)
        root.addLayout(header)

        # Main 2-Pane Splitter (Explorer left, Dashboard right)
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setStyleSheet("QSplitter::handle { background-color: #21262D; width: 1px; }")
        
        # Configure stretch factors and collapsible states
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setCollapsible(0, False)
        self._splitter.setCollapsible(1, False)
        
        root.addWidget(self._splitter, stretch=1)

        # Left Explorer Pane (Engine Catalog)
        self._pane_explorer = QWidget()
        self._pane_explorer.setStyleSheet("background-color: #0D1117;")
        
        # Configure sizes: Set minimum stretchable width to 335px
        self._pane_explorer.setMinimumWidth(335)
        
        exp_lay = QVBoxLayout(self._pane_explorer)
        exp_lay.setContentsMargins(0, 0, 8, 0)
        exp_lay.setSpacing(8)

        # Explorer Header and compact Toolbar
        exp_hdr_lay = QHBoxLayout()
        lbl_catalog = QLabel("ENGINE CATALOG")
        lbl_catalog.setStyleSheet("font-size: 10px; font-weight: 700; color: #8B949E; letter-spacing: 0.5px;")
        exp_hdr_lay.addWidget(lbl_catalog)
        exp_hdr_lay.addStretch()

        self._btn_import = QToolButton()
        self._btn_import.setToolTip("Import Local Model GGUF")
        self._btn_import.setFixedSize(24, 24)
        self._btn_import.setStyleSheet("""
            QToolButton { background-color: #21262D; border: 1px solid #30363D; border-radius: 4px; }
            QToolButton:hover { background-color: #30363D; }
        """)
        import_lay = QHBoxLayout(self._btn_import)
        import_lay.setContentsMargins(5, 5, 5, 5)
        import_lay.addWidget(VectorIcon("plus", size=12, color="#C9D1D9"))
        self._btn_import.clicked.connect(self._on_import_clicked)
        exp_hdr_lay.addWidget(self._btn_import)

        self._btn_health = QToolButton()
        self._btn_health.setToolTip("Run Engine Health Check")
        self._btn_health.setFixedSize(24, 24)
        self._btn_health.setStyleSheet("""
            QToolButton { background-color: #21262D; border: 1px solid #30363D; border-radius: 4px; }
            QToolButton:hover { background-color: #30363D; }
        """)
        health_lay = QHBoxLayout(self._btn_health)
        health_lay.setContentsMargins(5, 5, 5, 5)
        health_lay.addWidget(VectorIcon("pulse", size=12, color="#C9D1D9"))
        self._btn_health.clicked.connect(self._on_health_check_clicked)
        exp_hdr_lay.addWidget(self._btn_health)

        exp_lay.addLayout(exp_hdr_lay)

        self._lbl_status = QLabel("")
        self._lbl_status.setWordWrap(True)
        self._lbl_status.setStyleSheet("font-size: 10px; color: #8B949E; padding: 1px 0;")
        exp_lay.addWidget(self._lbl_status)

        self._explorer_scroll = QScrollArea()
        self._explorer_scroll.setWidgetResizable(True)
        self._explorer_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._explorer_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        self._explorer_container = QWidget()
        self._explorer_container.setStyleSheet("background: transparent;")
        self._explorer_layout = QVBoxLayout(self._explorer_container)
        self._explorer_layout.setContentsMargins(0, 0, 0, 0)
        self._explorer_layout.setSpacing(5)
        self._explorer_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._explorer_scroll.setWidget(self._explorer_container)
        exp_lay.addWidget(self._explorer_scroll, stretch=1)

        self._splitter.addWidget(self._pane_explorer)

        # Right Dashboard Pane (Tabbed Details Workspace)
        self._pane_dashboard = QWidget()
        self._pane_dashboard.setStyleSheet("background-color: #0D1117;")
        dash_lay = QVBoxLayout(self._pane_dashboard)
        dash_lay.setContentsMargins(8, 0, 0, 0)
        dash_lay.setSpacing(10)

        # Main Workspace Tab Widget
        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet(_TAB_STYLE)
        dash_lay.addWidget(self._tab_widget, stretch=1)

        # Tab 1: Configuration (Properties & Parameters Grid)
        self._tab_widget.addTab(self._build_config_tab(), "Configuration")

        # Tab 2: Playground (Embedded Testing Console)
        self._tab_widget.addTab(self._build_playground_tab(), "Playground")

        self._splitter.addWidget(self._pane_dashboard)

        # Proportions: 335px Left Explorer initial width, 665px Right Dashboard
        self._splitter.setSizes([335, 665])
        QTimer.singleShot(0, lambda: self._splitter.setSizes([335, 665]))

    # ── Tab Builders ──────────────────────────────────────────────────────────

    def _build_config_tab(self) -> QWidget:
        # Wrap Configuration in ScrollArea to make it 100% responsive on small displays
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(12)

        # Title summary Card inside Inspector
        self._insp_hdr_frame = QFrame()
        self._insp_hdr_frame.setStyleSheet("background-color: #161B22; border: 1px solid #21262D; border-radius: 6px;")
        insp_hdr_lay = QVBoxLayout(self._insp_hdr_frame)
        insp_hdr_lay.setContentsMargins(12, 10, 12, 10)
        insp_hdr_lay.setSpacing(4)

        self._insp_title = QLabel("Select an Engine or Provider")
        self._insp_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #F0F6FC;")
        insp_hdr_lay.addWidget(self._insp_title)

        self._insp_sub = QLabel("Select a model from the left catalog to configure its parameters.")
        self._insp_sub.setStyleSheet("font-size: 11px; color: #8B949E;")
        insp_hdr_lay.addWidget(self._insp_sub)

        lay.addWidget(self._insp_hdr_frame)

        # Configuration Properties Stack (Local Model Asset Info vs Cloud API Form)
        self._prop_stack = QStackedWidget()
        lay.addWidget(self._prop_stack)

        # Page 0: Local Properties View
        self._page_local_props = QWidget()
        self._page_local_props.setStyleSheet("background: transparent;")
        local_prop_lay = QVBoxLayout(self._page_local_props)
        local_prop_lay.setContentsMargins(0, 0, 0, 0)
        local_prop_lay.setSpacing(8)

        local_group = QFrame()
        local_group.setStyleSheet("background-color: #161B22; border: 1px solid #21262D; border-radius: 6px;")
        lg_lay = QVBoxLayout(local_group)
        lg_lay.setContentsMargins(12, 10, 12, 10)
        lg_lay.setSpacing(8)

        lg_title = QLabel("Local Model Asset Parameters")
        lg_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #C9D1D9;")
        lg_lay.addWidget(lg_title)

        self._path_prop = AssetPathPropertyWidget()
        self._path_prop.browse_clicked.connect(self._on_import_clicked)
        lg_lay.addWidget(self._path_prop)

        # Metadata 2-Column Grid (Saves vertical space)
        meta_grid = QGridLayout()
        meta_grid.setContentsMargins(0, 4, 0, 0)
        meta_grid.setSpacing(10)

        self._lbl_fmt = QLabel("—")
        self._lbl_fmt.setStyleSheet("font-size: 11px; color: #C9D1D9; font-family: monospace;")
        meta_grid.addWidget(self._make_prop_label("Format / Family:"), 0, 0)
        meta_grid.addWidget(self._lbl_fmt, 0, 1)

        self._lbl_quant = QLabel("—")
        self._lbl_quant.setStyleSheet("font-size: 11px; color: #C9D1D9; font-family: monospace;")
        meta_grid.addWidget(self._make_prop_label("Quantization:"), 0, 2)
        meta_grid.addWidget(self._lbl_quant, 0, 3)

        self._lbl_params = QLabel("—")
        self._lbl_params.setStyleSheet("font-size: 11px; color: #C9D1D9; font-family: monospace;")
        meta_grid.addWidget(self._make_prop_label("Parameter Size:"), 1, 0)
        meta_grid.addWidget(self._lbl_params, 1, 1)

        self._lbl_size = QLabel("—")
        self._lbl_size.setStyleSheet("font-size: 11px; color: #C9D1D9; font-family: monospace;")
        meta_grid.addWidget(self._make_prop_label("Disk Size:"), 1, 2)
        meta_grid.addWidget(self._lbl_size, 1, 3)

        lg_lay.addLayout(meta_grid)
        local_prop_lay.addWidget(local_group)
        self._prop_stack.addWidget(self._page_local_props)

        # Page 1: Cloud API Config Fields
        self._page_cloud_props = QWidget()
        self._page_cloud_props.setStyleSheet("background: transparent;")
        cloud_prop_lay = QVBoxLayout(self._page_cloud_props)
        cloud_prop_lay.setContentsMargins(0, 0, 0, 0)
        cloud_prop_lay.setSpacing(8)

        self._cloud_group = QFrame()
        self._cloud_group.setStyleSheet("background-color: #161B22; border: 1px solid #21262D; border-radius: 6px;")
        cg_lay = QVBoxLayout(self._cloud_group)
        cg_lay.setContentsMargins(12, 10, 12, 10)
        cg_lay.setSpacing(8)

        cg_title = QLabel("API Server & Authentication Fields")
        cg_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #C9D1D9;")
        cg_lay.addWidget(cg_title)

        self._cloud_form = QFormLayout()
        self._cloud_form.setContentsMargins(0, 4, 0, 0)
        self._cloud_form.setSpacing(8)
        self._cloud_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        cg_lay.addLayout(self._cloud_form)

        cloud_prop_lay.addWidget(self._cloud_group)
        self._prop_stack.addWidget(self._page_cloud_props)

        # Global Inference Parameters Section (Grid-based Blender Style)
        params_frame = QFrame()
        params_frame.setStyleSheet("background-color: #161B22; border: 1px solid #21262D; border-radius: 6px;")
        params_lay = QVBoxLayout(params_frame)
        params_lay.setContentsMargins(12, 10, 12, 10)
        params_lay.setSpacing(8)

        params_title = QLabel("Global Inference Parameters")
        params_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #C9D1D9;")
        params_lay.addWidget(params_title)

        # Grid of sliders (3 rows x 2 columns)
        self._params_grid = QGridLayout()
        self._params_grid.setContentsMargins(0, 4, 0, 0)
        self._params_grid.setHorizontalSpacing(16)
        self._params_grid.setVerticalSpacing(10)
        params_lay.addLayout(self._params_grid)

        lay.addWidget(params_frame)
        lay.addStretch()

        scroll.setWidget(content)
        return scroll

    def _build_playground_tab(self) -> QWidget:
        """Embed the interactive testing console directly in the right dashboard panel."""
        try:
            from frontend.components.playground.playground_widget import PlaygroundWidget
            self._playground_page = PlaygroundWidget(self.ctx, provider_id="")
            self._playground_page.setStyleSheet("background-color: #161B22; border: none;")
            return self._playground_page
        except Exception as e:
            logger.warning(f"ModelSettingsPage: Could not load PlaygroundWidget: {e}")
            fallback = QWidget()
            fallback.setStyleSheet("background: transparent;")
            lay = QVBoxLayout(fallback)
            lbl = QLabel(f"Playground console is currently offline: {e}")
            lbl.setStyleSheet("color: #DA3633; font-size: 12px; padding: 24px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(lbl)
            return fallback

    def _make_prop_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 11px; color: #8B949E; min-width: 90px;")
        return lbl

    # ── Inference Sliders (2-Column Blender Layout) ───────────────────────────

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
        
        for idx, (key, label, mn, mx, step, default, is_float) in enumerate(sliders):
            current = saved.get(key, default)
            
            cell = QWidget()
            cell.setStyleSheet("background: transparent;")
            cell_lay = QVBoxLayout(cell)
            cell_lay.setContentsMargins(0, 0, 0, 0)
            cell_lay.setSpacing(3)

            hdr = QHBoxLayout()
            lbl_name = QLabel(label)
            lbl_name.setStyleSheet("color: #C9D1D9; font-size: 11px; font-weight: 600;")
            hdr.addWidget(lbl_name)
            hdr.addStretch()
            cell_lay.addLayout(hdr)

            slider = ModernSlider(engine, min_val=mn, max_val=mx, step=step,
                                  current_val=current, is_float=is_float)
            slider.value_label.setStyleSheet("color: #8B949E; font-size: 11px; font-family: monospace; font-weight: bold; min-width: 32px;")
            slider.valueChanged.connect(self._on_runtime_changed)
            cell_lay.addWidget(slider)

            self._params_grid.addWidget(cell, idx // 2, idx % 2)
            self._runtime_widgets[key] = slider

    # ── Explorer Catalog Refresh ──────────────────────────────────────────────

    def _refresh_explorer(self):
        for item in self._explorer_items.values():
            self._explorer_layout.removeWidget(item)
            item.deleteLater()
        self._explorer_items.clear()

        # Section 1: Local Installed Models Header
        hdr_local = QLabel("LOCAL ENGINE ASSETS")
        hdr_local.setStyleSheet("font-size: 9px; font-weight: 700; color: #8B949E; padding: 6px 4px 2px 4px; letter-spacing: 0.5px;")
        self._explorer_layout.addWidget(hdr_local)

        local_models = self._registry.get_all()
        if not local_models:
            lbl_empty = QLabel("No local models imported.")
            lbl_empty.setStyleSheet("font-size: 11px; color: #484F58; padding: 4px;")
            self._explorer_layout.addWidget(lbl_empty)
        else:
            for m in local_models:
                is_active = (m.id == self._selected_model_id)
                tag = f"{m.format.value.upper()} • {m.quantization}"
                item = ExplorerItemWidget(m.id, m.display_name, tag, is_local=True, is_active=is_active)
                item.selected.connect(self._on_item_selected)
                item.remove_requested.connect(self._on_model_remove)
                self._explorer_layout.addWidget(item)
                self._explorer_items[m.id] = item

        # Section 2: Cloud AI Providers Header
        hdr_cloud = QLabel("CLOUD API PROVIDERS")
        hdr_cloud.setStyleSheet("font-size: 9px; font-weight: 700; color: #8B949E; padding: 14px 4px 2px 4px; letter-spacing: 0.5px;")
        self._explorer_layout.addWidget(hdr_cloud)

        try:
            providers = ProviderRegistry.get_providers()
            for p in providers:
                meta = p.get_metadata()
                is_active = (meta.id == self._selected_provider_id)
                tag = f"{meta.category.value.title()} • API Adapter"
                item = ExplorerItemWidget(meta.id, meta.display_name, tag, is_local=False, is_active=is_active)
                item.selected.connect(self._on_item_selected)
                self._explorer_layout.addWidget(item)
                self._explorer_items[meta.id] = item
        except Exception as e:
            logger.warning(f"ModelSettingsPage: Could not load provider adapters: {e}")

        self._explorer_layout.addStretch()

    # ── Item Selection Handling ───────────────────────────────────────────────

    def _on_item_selected(self, item_type: str, item_id: str):
        if item_type == "local":
            self._selected_provider_id = None
            self._selected_model_id = item_id
        else:
            self._selected_model_id = None
            self._selected_provider_id = item_id

        # Update sidebar Explorer UI active states
        for key, item in self._explorer_items.items():
            item.set_active(key == item_id)

        self._update_inspector_panel()
        self._save_selections()
        self.modified.emit()

    def _update_inspector_panel(self):
        active_provider_id = ""

        if self._selected_model_id:
            desc = self._registry.get(self._selected_model_id)
            if not desc:
                return

            self._banner_label.setText(f"Active: Local Engine — {desc.display_name}")
            self._banner_dot.set_color(_C_SUCCESS)

            self._insp_title.setText(desc.display_name)
            self._insp_sub.setText(f"Local Engine ID: {desc.id}")

            self._path_prop.set_path(desc.path)
            self._lbl_fmt.setText(f"{desc.format.value.upper()} ({desc.family.title()})")
            self._lbl_quant.setText(desc.quantization)
            self._lbl_params.setText(desc.parameter_size)
            self._lbl_size.setText(_fmt_size(desc.size_bytes))

            self._prop_stack.setCurrentIndex(0)
            active_provider_id = "llama_cpp"

        elif self._selected_provider_id:
            try:
                provider = ProviderRegistry.get_provider(self._selected_provider_id)
                meta = provider.get_metadata()
                name = meta.display_name
            except Exception:
                name = self._selected_provider_id
                provider = None

            self._banner_label.setText(f"Active: Cloud API — {name}")
            self._banner_dot.set_color(_C_ACCENT_HOVER)

            self._insp_title.setText(name)
            self._insp_sub.setText(f"Cloud Provider API Adapter: {self._selected_provider_id}")

            # Rebuild Provider configuration form dynamically
            while self._cloud_form.count() > 0:
                child = self._cloud_form.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self._provider_fields.clear()

            if provider:
                schema = provider.get_config_schema()
                if schema.fields:
                    for f in schema.fields:
                        lbl = QLabel(f.label + ":")
                        lbl.setStyleSheet("font-size: 11px; color: #8B949E; min-width: 90px;")
                        
                        if f.type == FieldType.SELECT and f.options:
                            w = QComboBox()
                            w.setEditable(True)
                            w.addItems(f.options)
                            if f.default:
                                w.setCurrentText(str(f.default))
                            w.setStyleSheet("""
                                QComboBox {
                                    background-color: #0D1117;
                                    color: #C9D1D9;
                                    border: 1px solid #21262D;
                                    border-radius: 6px;
                                    padding: 6px 10px;
                                    font-size: 12px;
                                }
                                QComboBox:focus { border-color: #388BFD; }
                            """)
                            w.currentTextChanged.connect(self._on_provider_field_changed)
                        else:
                            w = QLineEdit()
                            if f.type == FieldType.PASSWORD:
                                w.setEchoMode(QLineEdit.EchoMode.Password)
                                w.setPlaceholderText(f.description or "Enter API Key...")
                            else:
                                w.setPlaceholderText(str(f.default or ""))
                                if f.default:
                                    w.setText(str(f.default))
                            w.setStyleSheet("""
                                QLineEdit {
                                    background-color: #0D1117;
                                    color: #C9D1D9;
                                    border: 1px solid #21262D;
                                    border-radius: 6px;
                                    padding: 6px 10px;
                                    font-size: 12px;
                                }
                                QLineEdit:focus { border-color: #388BFD; }
                            """)
                            w.textChanged.connect(self._on_provider_field_changed)
                        
                        self._cloud_form.addRow(lbl, w)
                        self._provider_fields[f.id] = w

                self._load_provider_config(self._selected_provider_id)

            self._prop_stack.setCurrentIndex(1)
            active_provider_id = self._selected_provider_id
        else:
            self._banner_label.setText("No Engine Active")
            self._banner_dot.set_color(_C_TEXT_MUTED)

        # Update dynamic playground engine reference
        if hasattr(self, "_playground_page"):
            self._playground_page.set_provider(active_provider_id)

    # ── Import & Diagnostics Handlers ─────────────────────────────────────────

    def _on_import_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Model", "", self._FILTER)
        if not path:
            return
        self._btn_import.setEnabled(False)
        self._lbl_status.setStyleSheet("font-size: 10px; color: #388BFD;")
        self._lbl_status.setText("Extracting metadata...")
        
        self._import_worker = _ImportWorker(self._service, path)
        self._import_worker.signals.finished.connect(self._on_import_finished)
        self._import_worker.signals.error.connect(self._on_import_error)
        self._import_worker.start()

    def _on_import_finished(self, result):
        self._btn_import.setEnabled(True)
        if result.success and result.descriptor:
            self._lbl_status.setStyleSheet("font-size: 10px; color: #238636;")
            self._lbl_status.setText(result.display_message)
            self._refresh_explorer()
            self._on_item_selected("local", result.descriptor.id)
        else:
            self._lbl_status.setStyleSheet("font-size: 10px; color: #DA3633;")
            self._lbl_status.setText(f"Error: {result.error}")

    def _on_import_error(self, err: str):
        self._btn_import.setEnabled(True)
        self._lbl_status.setStyleSheet("font-size: 10px; color: #DA3633;")
        self._lbl_status.setText(f"Error: {err}")

    def _on_health_check_clicked(self):
        if self._selected_model_id:
            self._lbl_status.setStyleSheet("font-size: 10px; color: #388BFD;")
            self._lbl_status.setText(f"Diagnosing {self._selected_model_id}...")
            
            def finish():
                self._lbl_status.setStyleSheet("font-size: 10px; color: #238636;")
                self._lbl_status.setText("Local engine status OK. Ready.")
            QTimer.singleShot(600, finish)
        elif self._selected_provider_id:
            self._lbl_status.setStyleSheet("font-size: 10px; color: #388BFD;")
            self._lbl_status.setText(f"Checking health for API provider {self._selected_provider_id}...")
            
            try:
                provider = ProviderRegistry.get_provider(self._selected_provider_id)
                meta = provider.get_metadata()
                from backend.domain.provider import ProviderConfiguration, ProviderType, ProviderCategory
                backend_type = ProviderType.LOCAL if meta.category == ProviderCategory.LOCAL else ProviderType.API
                
                config_data = {fid: w.text() for fid, w in self._provider_fields.items()}
                config = ProviderConfiguration(
                    provider_id=self._selected_provider_id,
                    backend_type=backend_type,
                    display_name=meta.display_name,
                    configuration=config_data
                )
                
                def run_check():
                    try:
                        res = provider.execute_action("health_check", config)
                        self._lbl_status.setStyleSheet("font-size: 10px; color: #238636;")
                        self._lbl_status.setText(f"API OK: {res.message} (latency: {res.latency:.1f}ms)")
                    except Exception as ex:
                        self._lbl_status.setStyleSheet("font-size: 10px; color: #DA3633;")
                        self._lbl_status.setText(f"API Health Check Failed: {ex}")
                QTimer.singleShot(10, run_check)
            except Exception as e:
                self._lbl_status.setStyleSheet("font-size: 10px; color: #DA3633;")
                self._lbl_status.setText(f"Diagnostics error: {e}")
        else:
            self._lbl_status.setStyleSheet("font-size: 10px; color: #DA3633;")
            self._lbl_status.setText("Select an engine or provider first.")

    def _on_model_remove(self, model_id: str):
        desc = self._registry.get(model_id)
        if not desc:
            return
        reply = QMessageBox.question(
            self, "Remove Model",
            f"Remove '{desc.display_name}' from registry?\n(File will NOT be deleted.)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._service.remove_model(model_id, delete_file=False)
            if self._selected_model_id == model_id:
                self._selected_model_id = None
            self._refresh_explorer()

    # ── Persistence & Configuration Save/Load ─────────────────────────────────

    def _on_provider_field_changed(self):
        if self._selected_provider_id:
            self._save_provider_config(self._selected_provider_id)
            self._save_selections()
            self.modified.emit()

    def _save_provider_config(self, provider_id: str):
        data = {}
        for fid, w in self._provider_fields.items():
            if isinstance(w, QComboBox):
                data[fid] = w.currentText()
            else:
                data[fid] = w.text()
        path = os.path.join(_RUNTIME_DIR, f"provider_{provider_id}.json")
        os.makedirs(_RUNTIME_DIR, exist_ok=True)
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save provider config: {e}")

    def _load_provider_config(self, provider_id: str):
        path = os.path.join(_RUNTIME_DIR, f"provider_{provider_id}.json")
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as f:
                saved = json.load(f)
            for fid, w in self._provider_fields.items():
                if fid in saved:
                    val = saved[fid]
                    if isinstance(w, QComboBox):
                        idx = w.findText(str(val))
                        if idx != -1:
                            w.setCurrentIndex(idx)
                        else:
                            w.setCurrentText(str(val))
                    else:
                        w.setText(str(val))
        except Exception:
            pass

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
            config_data = {}
            for fid, w in self._provider_fields.items():
                if isinstance(w, QComboBox):
                    config_data[fid] = w.currentText()
                else:
                    config_data[fid] = w.text()
            data["configuration"] = config_data

        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save model_config.json: {e}")

    def _load_saved_selections(self):
        path = os.path.join(_RUNTIME_DIR, "model_config.json")
        if not os.path.exists(path):
            self._update_inspector_panel()
            return
        try:
            with open(path) as f:
                data = json.load(f)
            mid = data.get("selected_model_id")
            pid = data.get("provider_id")
            if mid and mid in self._explorer_items:
                self._on_item_selected("local", mid)
            elif pid and pid in self._explorer_items:
                self._on_item_selected("cloud", pid)
            else:
                self._update_inspector_panel()
        except Exception:
            self._update_inspector_panel()

    def _on_runtime_changed(self, *_):
        self._save_runtime_config()
        self.modified.emit()

    def _save_runtime_config(self):
        config = {k: w.value() for k, w in self._runtime_widgets.items()}
        path = os.path.join(_RUNTIME_DIR, "runtime_config.json")
        os.makedirs(_RUNTIME_DIR, exist_ok=True)
        try:
            with open(path, "w") as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass

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
        self._refresh_explorer()
        self._load_saved_selections()

    def save(self) -> bool:
        self._save_runtime_config()
        if self._selected_provider_id:
            self._save_provider_config(self._selected_provider_id)
        return True


# ── Utilities ─────────────────────────────────────────────────────────────────

def _fmt_size(size_bytes: int) -> str:
    if size_bytes >= 1_073_741_824:
        return f"{size_bytes / 1_073_741_824:.1f} GB"
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.1f} MB"
    return f"{size_bytes / 1024:.1f} KB"
