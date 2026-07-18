from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFormLayout
from PySide6.QtCore import Qt, Signal
from frontend.core.app_context import AppContext
from backend.core.provider_registry import ProviderRegistry
from backend.domain.provider import FieldType, AIProvider

class ModelSettingsPage(QWidget):
    """
    AI Control Center.
    Dynamically generated based on Provider Registry capabilities and schemas.
    """
    
    modified = Signal()
    
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self._current_provider_id = None
        self._dynamic_widgets = {}
        
        self._build_ui()
        self.reload()
        
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)
        root.setSpacing(32)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title = QLabel("Model Settings")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #E2E8F0;")
        root.addWidget(title)
        
        from frontend.components.modern.settings_card import SettingsCard
        
        # Card 1: AI Backend
        self.backend_card = SettingsCard("AI Backend", "Select the model provider for your interviews.")
        
        self.provider_combo = QComboBox()
        self.provider_combo.setStyleSheet("""
            QComboBox {
                background-color: #0F1115;
                color: #E2E8F0;
                border: 1px solid #272A30;
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 36px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox:hover { border: 1px solid #3A414D; }
            QComboBox:focus { border: 1px solid #3B82F6; }
        """)
        
        providers = ProviderRegistry.get_providers()
        for p in providers:
            self.provider_combo.addItem(p.name, p.id)
            
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        self.backend_card.addWidget(self.provider_combo)
        root.addWidget(self.backend_card)
        
        # Card 2: Configuration
        self.config_card = SettingsCard("Provider Configuration", "Configure API keys and specific settings for the selected provider.")
        self.config_container = QWidget()
        self.config_layout = QFormLayout(self.config_container)
        self.config_layout.setContentsMargins(0, 0, 0, 0)
        self.config_layout.setSpacing(16)
        # Style form layout labels
        self.config_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.config_card.addWidget(self.config_container)
        root.addWidget(self.config_card)
        
        # Card 3: Runtime
        self.runtime_card = SettingsCard("Runtime Parameters", "Adjust model sampling and context limits.")
        self.runtime_container = QWidget()
        self.runtime_layout = QFormLayout(self.runtime_container)
        self.runtime_layout.setContentsMargins(0, 0, 0, 0)
        self.runtime_layout.setSpacing(16)
        self.runtime_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.runtime_card.addWidget(self.runtime_container)
        root.addWidget(self.runtime_card)
        
        # Card 4: Diagnostics
        self.diag_card = SettingsCard("Diagnostics", "View connection status and capabilities.")
        self.diag_container = QWidget()
        from PySide6.QtWidgets import QGridLayout
        self.diag_layout = QGridLayout(self.diag_container)
        self.diag_layout.setContentsMargins(0, 0, 0, 0)
        self.diag_layout.setSpacing(24)
        self.diag_card.addWidget(self.diag_container)
        root.addWidget(self.diag_card)
        
        root.addStretch()
        
    def reload(self):
        # Load from stored settings (dummy for now)
        saved_provider = "openai" 
        index = self.provider_combo.findData(saved_provider)
        if index >= 0:
            self.provider_combo.blockSignals(True)
            self.provider_combo.setCurrentIndex(index)
            self.provider_combo.blockSignals(False)
            self._render_provider_ui(saved_provider)
            
    def save(self):
        pass # In a real implementation, we save the dynamic widget values
        
    def _on_provider_changed(self, index):
        provider_id = self.provider_combo.itemData(index)
        self._render_provider_ui(provider_id)
        self.modified.emit()
        
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def _render_provider_ui(self, provider_id: str):
        self._clear_layout(self.config_layout)
        self._clear_layout(self.runtime_layout)
        self._clear_layout(self.diag_layout)
        self._dynamic_widgets.clear()
        
        provider = ProviderRegistry.get_provider(provider_id)
        schema = provider.get_config_schema()
        caps = provider.get_capabilities()
        
        # Render Schema Fields
        for field in schema.fields:
            if field.type == FieldType.TEXT or field.type == FieldType.PASSWORD:
                widget = self.ctx.ui.make_input(placeholder=field.default or "")
                if field.type == FieldType.PASSWORD:
                    widget.line_edit.setEchoMode(widget.line_edit.EchoMode.Password)
                widget.textChanged.connect(lambda text: self.modified.emit())
            elif field.type == FieldType.SELECT:
                widget = QComboBox()
                widget.addItems(field.options or [])
                widget.setStyleSheet("""
                    QComboBox {
                        background-color: #0F1115;
                        color: #E2E8F0;
                        border: 1px solid #272A30;
                        border-radius: 6px;
                        padding: 8px 12px;
                        min-height: 36px;
                    }
                    QComboBox::drop-down { border: none; }
                """)
                widget.currentIndexChanged.connect(lambda idx: self.modified.emit())
            else:
                widget = self.ctx.ui.make_input()
                
            lbl = QLabel(field.label)
            lbl.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 500;")
            self.config_layout.addRow(lbl, widget)
            self._dynamic_widgets[field.id] = widget
            
        # Render Runtime Parameters based on Capabilities
        from frontend.components.modern.modern_slider import ModernSlider
        
        # Temperature
        lbl_temp = QLabel("Temperature")
        lbl_temp.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 500;")
        widget_temp = ModernSlider(self.ctx.ui._engine, min_val=0.0, max_val=2.0, step=0.1, current_val=0.7, is_float=True)
        widget_temp.valueChanged.connect(lambda val: self.modified.emit())
        self.runtime_layout.addRow(lbl_temp, widget_temp)
        
        # Top P
        lbl_top_p = QLabel("Top P")
        lbl_top_p.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 500;")
        widget_top_p = ModernSlider(self.ctx.ui._engine, min_val=0.0, max_val=1.0, step=0.05, current_val=0.9, is_float=True)
        widget_top_p.valueChanged.connect(lambda val: self.modified.emit())
        self.runtime_layout.addRow(lbl_top_p, widget_top_p)
        
        # Context Length
        lbl_ctx = QLabel("Context Length")
        lbl_ctx.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 500;")
        max_ctx = caps.max_context_length if caps.max_context_length else 8192
        current_ctx = min(8192, max_ctx)
        widget_ctx = ModernSlider(self.ctx.ui._engine, min_val=512, max_val=max_ctx, step=512, current_val=current_ctx, is_float=False)
        widget_ctx.valueChanged.connect(lambda val: self.modified.emit())
        self.runtime_layout.addRow(lbl_ctx, widget_ctx)
        
        # Max Output Tokens
        lbl_out = QLabel("Max Output Tokens")
        lbl_out.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 500;")
        max_out = caps.max_output_tokens if caps.max_output_tokens else 4096
        current_out = min(2048, max_out)
        widget_out = ModernSlider(self.ctx.ui._engine, min_val=128, max_val=max_out, step=128, current_val=current_out, is_float=False)
        widget_out.valueChanged.connect(lambda val: self.modified.emit())
        self.runtime_layout.addRow(lbl_out, widget_out)
            
        # Render Diagnostics
        diags = [
            ("Provider Type", provider.provider_type.value.upper()),
            ("Streaming Support", "Supported" if caps.supports_streaming else "Not Supported"),
            ("JSON Mode", "Supported" if caps.supports_json_mode else "Not Supported"),
            ("Function Calling", "Supported" if caps.supports_function_calling else "Not Supported"),
            ("Vision", "Supported" if caps.supports_vision else "Not Supported"),
            ("Status", "✓ Connected")
        ]
        
        row, col = 0, 0
        for label_text, val in diags:
            info_row = QWidget()
            info_layout = QVBoxLayout(info_row)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(4)
            
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #94A3B8; font-size: 12px;")
            val_lbl = QLabel(val)
            
            if "Connected" in val or "Supported" in val:
                color = "#48BB78"
            elif "Not Supported" in val:
                color = "#F56565"
            else:
                color = "#E2E8F0"
                
            val_lbl.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 600;")
            
            info_layout.addWidget(lbl)
            info_layout.addWidget(val_lbl)
            
            self.diag_layout.addWidget(info_row, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
