from PySide6.QtWidgets import QWidget, QHBoxLayout, QSlider, QLabel
from PySide6.QtCore import Qt, Signal
from frontend.engine import StyleEngine

class NoScrollSlider(QSlider):
    def wheelEvent(self, event):
        event.ignore()

class ModernSlider(QWidget):
    valueChanged = Signal(float)

    def __init__(self, engine: StyleEngine, min_val: float, max_val: float, step: float, current_val: float, is_float: bool = False, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.is_float = is_float
        
        # Scaling factor for float representation in integer-based QSlider
        self.scale_factor = 100 if is_float else 1
        
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        
        self.slider = NoScrollSlider(Qt.Orientation.Horizontal)
        self.slider.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.slider.setMinimum(int(self.min_val * self.scale_factor))
        self.slider.setMaximum(int(self.max_val * self.scale_factor))
        self.slider.setSingleStep(int(self.step * self.scale_factor))
        self.slider.setPageStep(int(self.step * self.scale_factor * 5))
        self.slider.setValue(int(current_val * self.scale_factor))
        
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border-radius: 4px;
                height: 8px;
                background: #1E293B;
            }
            QSlider::sub-page:horizontal {
                background: #3B82F6;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #E2E8F0;
                width: 16px;
                height: 16px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #FFFFFF;
            }
        """)
        
        self.value_label = QLabel()
        self.value_label.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 500; min-width: 48px;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self._update_label(self.slider.value())
        
        self.slider.valueChanged.connect(self._on_value_changed)
        
        layout.addWidget(self.slider, stretch=1)
        layout.addWidget(self.value_label)
        
    def _on_value_changed(self, int_val):
        self._update_label(int_val)
        self.valueChanged.emit(self.value())
        
    def _update_label(self, int_val):
        val = int_val / self.scale_factor
        if self.is_float:
            self.value_label.setText(f"{val:.2f}")
        else:
            self.value_label.setText(f"{int(val)}")
            
    def value(self) -> float:
        return self.slider.value() / self.scale_factor
        
    def set_value(self, val: float):
        self.slider.setValue(int(val * self.scale_factor))
