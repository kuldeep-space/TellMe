"""
CRTOverlay — QPainter-based scanline + vignette effect overlay.

Rendered as a transparent top-level child widget covering the MainWindow.
Never reduces readability (alpha is intentionally very low).
Fully disableable via Settings.
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QRectF, QTimer
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QPen
import random


class CRTOverlay(QWidget):
    """
    Transparent overlay widget rendering:
    - Scanlines (very faint horizontal lines)
    - Vignette (radial darkening at edges)
    - Optional subtle flicker
    """

    def __init__(self, parent: QWidget, *, scanlines: bool = True,
                 vignette: bool = True, flicker: bool = False):
        super().__init__(parent)
        self._scanlines = scanlines
        self._vignette  = vignette
        self._flicker   = flicker
        self._alpha_offset = 0

        # Transparent passthrough
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Resize to always cover parent
        parent.installEventFilter(self)

        if flicker:
            self._flicker_timer = QTimer(self)
            self._flicker_timer.timeout.connect(self._flick)
            self._flicker_timer.start(80)

    def _flick(self):
        self._alpha_offset = random.choice([0, 0, 0, 2, -2, 0])
        self.update()

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.Type.Resize:
            self.resize(obj.size())
        return False

    def paintEvent(self, _):
        if not (self._scanlines or self._vignette):
            return

        w = self.width()
        h = self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        # ── Scanlines ─────────────────────────────────────────────────
        if self._scanlines:
            line_alpha = max(0, 18 + self._alpha_offset)
            pen = QPen(QColor(0, 0, 0, line_alpha))
            pen.setWidth(1)
            painter.setPen(pen)
            y = 0
            while y < h:
                painter.drawLine(0, y, w, y)
                y += 3   # every 3rd pixel = 1 scanline per 3 rows

        # ── Vignette ──────────────────────────────────────────────────
        if self._vignette:
            grad = QRadialGradient(w / 2, h / 2, max(w, h) * 0.7)
            grad.setColorAt(0.0, QColor(0, 0, 0, 0))
            grad.setColorAt(0.6, QColor(0, 0, 0, 0))
            grad.setColorAt(1.0, QColor(0, 0, 0, 60))
            painter.setPen(Qt.PenStyle.NoPen)
            from PySide6.QtGui import QBrush
            painter.setBrush(QBrush(grad))
            painter.drawRect(0, 0, w, h)

        painter.end()

    # ── Public API ────────────────────────────────────────────────────
    def set_scanlines(self, value: bool):
        self._scanlines = value
        self.update()

    def set_vignette(self, value: bool):
        self._vignette = value
        self.update()

    def set_flicker(self, value: bool):
        self._flicker = value
        if value and not hasattr(self, "_flicker_timer"):
            self._flicker_timer = QTimer(self)
            self._flicker_timer.timeout.connect(self._flick)
        if value:
            self._flicker_timer.start(80)
        elif hasattr(self, "_flicker_timer"):
            self._flicker_timer.stop()
