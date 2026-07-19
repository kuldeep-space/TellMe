"""
MascotWidget — Procedural AI Interviewer Character Renderer.
Receives target MascotSnapshots and performs smooth animations,
blending, and procedural painting using QPainter.
"""
from __future__ import annotations

import math
import random
from typing import Optional, Tuple

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import (
    QPainter, QColor, QPainterPath,
    QLinearGradient, QRadialGradient, QPen, QBrush, QCursor
)
from PySide6.QtWidgets import QWidget, QSizePolicy

from frontend.components.mascot.mascot_state import (
    MascotEmotion, MascotActivity, MascotPresence, MascotSnapshot,
    _COLOR_BLUE_PRIMARY, _COLOR_BLUE_SECONDARY, _COLOR_BLUE_GLOW, _COLOR_BLUE_PULSE
)
from frontend.components.mascot.mascot_controller import MascotController

# ── Stylistic Palette constants ─────────────────────────────────
_COL_MOUTH    = QColor(122, 96, 112)
_DARK_BG      = QColor(14, 16, 26)
_HAIR_DARK    = QColor(14, 15, 24)
_HAIR_MID     = QColor(28, 30, 46)


class MascotWidget(QWidget):
    """
    Pure procedural animated AI Interviewer widget.
    Receives target parameters via MascotSnapshot and interpolates values.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # ── Controller & Target snapshot ─────────────────────────
        self.controller = MascotController()
        self.controller.initialize()
        self._target_snapshot: Optional[MascotSnapshot] = None

        # ── Current animated values (for smooth lerping) ──────────
        self._current_mouth_curve: float = 0.3
        self._current_brow_raise: float = 0.0
        self._current_brow_furrow: float = 0.0
        self._current_mouth_open: float = 0.0
        self._current_head_tilt: float = 0.0
        self._current_glow_intensity: float = 1.0
        self._current_blink_rate: float = 1.0
        self._current_breathe_amp: float = 1.0
        self._current_breathe_speed_mult: float = 1.0
        self._current_eye_wander_mult: float = 1.0

        # Current colors
        self._current_primary_accent: QColor = _COLOR_BLUE_PRIMARY
        self._current_secondary_accent: QColor = _COLOR_BLUE_SECONDARY
        self._current_eye_glow: QColor = _COLOR_BLUE_GLOW
        self._current_pulse_color: QColor = _COLOR_BLUE_PULSE

        # ── Animation time ───────────────────────────────────────
        self._t: float = 0.0
        self._speak_phase: float = 0.0
        self._node_pulse: float = 0.0

        # ── Blink ───────────────────────────────────────────────
        self._blink_phase: float = 0.0
        self._blink_step: int = 0
        self._BLINK_STEPS = 12

        # ── Eye Tracking ────────────────────────────────────────
        self._eye_ox: float = 0.0
        self._eye_oy: float = 0.0
        self._eye_tx: float = 0.0
        self._eye_ty: float = 0.0

        # ── Timers ──────────────────────────────────────────────
        # Main 60fps update loop
        self._main_timer = QTimer(self)
        self._main_timer.timeout.connect(self._tick)
        self._main_timer.start(16)

        # Blink animation timer
        self._blink_anim = QTimer(self)
        self._blink_anim.timeout.connect(self._blink_frame)

        # Blink scheduler
        self._blink_sched = QTimer(self)
        self._blink_sched.setSingleShot(True)
        self._blink_sched.timeout.connect(self._do_blink)
        self._schedule_blink()

        # Eye wander scheduler
        self._wander_timer = QTimer(self)
        self._wander_timer.setSingleShot(True)
        self._wander_timer.timeout.connect(self._wander)
        self._wander_timer.start(2200)

        # Widget styling
        self.setMinimumSize(200, 260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background: transparent;")
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

    def set_target_snapshot(self, snapshot: MascotSnapshot) -> None:
        """Expose snapshot target for render loop."""
        self._target_snapshot = snapshot

    # ── Animation Ticks ──────────────────────────────────────────────────

    def _tick(self) -> None:
        dt = 0.016
        self._t += dt
        self._node_pulse = 0.5 + 0.5 * math.sin(self._t * 2.5)

        # Drive controller tick
        snap = self.controller.update(dt)
        self.set_target_snapshot(snap)

        # 1. Update interpolation towards target snapshot
        if self._target_snapshot:
            snap = self._target_snapshot
            spd = snap.transition_speed

            self._current_mouth_curve += (snap.mouth_curve - self._current_mouth_curve) * spd
            self._current_brow_raise += (snap.brow_raise - self._current_brow_raise) * spd
            self._current_brow_furrow += (snap.brow_furrow - self._current_brow_furrow) * spd
            self._current_mouth_open += (snap.mouth_open - self._current_mouth_open) * spd
            self._current_head_tilt += (snap.head_tilt - self._current_head_tilt) * spd
            self._current_glow_intensity += (snap.glow_intensity - self._current_glow_intensity) * spd
            self._current_blink_rate += (snap.blink_rate - self._current_blink_rate) * spd
            self._current_breathe_amp += (snap.breathe_amp - self._current_breathe_amp) * spd
            self._current_breathe_speed_mult += (snap.breathe_speed_mult - self._current_breathe_speed_mult) * spd
            self._current_eye_wander_mult += (snap.eye_wander_mult - self._current_eye_wander_mult) * spd

            # Color lerps
            self._current_primary_accent = self._lerp_color(self._current_primary_accent, snap.primary_accent, spd)
            self._current_secondary_accent = self._lerp_color(self._current_secondary_accent, snap.secondary_accent, spd)
            self._current_eye_glow = self._lerp_color(self._current_eye_glow, snap.eye_glow, spd)
            self._current_pulse_color = self._lerp_color(self._current_pulse_color, snap.pulse_color, spd)

        # 2. Update active activities
        is_speaking = False
        if self._target_snapshot:
            is_speaking = (self._target_snapshot.activity == MascotActivity.SPEAKING)

        if is_speaking:
            self._speak_phase += 0.24
        else:
            self._speak_phase = 0.0

        # 3. Cursor-based eye tracking
        w, h = self.width(), self.height()
        pos = self.mapFromGlobal(QCursor.pos())
        face_cx, face_cy = w * 0.5, h * 0.40
        dx = (pos.x() - face_cx) * 0.032
        dy = (pos.y() - face_cy) * 0.032
        max_m = 3.5
        dist = math.hypot(dx, dy)
        if dist > max_m:
            dx, dy = dx / dist * max_m, dy / dist * max_m

        # Target offsets
        self._eye_tx = dx * 0.55 + self._eye_ox * 0.1
        self._eye_ty = dy * 0.55 + self._eye_oy * 0.1

        # Smooth follow
        self._eye_ox += (self._eye_tx - self._eye_ox) * 0.065
        self._eye_oy += (self._eye_ty - self._eye_oy) * 0.065

        self.update()

    def _lerp_color(self, cur: QColor, target: QColor, spd: float) -> QColor:
        r = cur.red() + (target.red() - cur.red()) * spd
        g = cur.green() + (target.green() - cur.green()) * spd
        b = cur.blue() + (target.blue() - cur.blue()) * spd
        a = cur.alpha() + (target.alpha() - cur.alpha()) * spd
        return QColor(int(max(0, min(255, r))), int(max(0, min(255, g))), int(max(0, min(255, b))), int(max(0, min(255, a))))

    # ── Blinking Animation ────────────────────────────────────────────────

    def _schedule_blink(self) -> None:
        rate = self._current_blink_rate
        base = int(3600 / max(0.1, rate))
        delay = random.randint(int(base * 0.5), int(base * 1.65))
        self._blink_sched.start(delay)

    def _do_blink(self) -> None:
        if not self._blink_anim.isActive():
            self._blink_phase = 0.0
            self._blink_step = 0
            self._blink_anim.start(13)

    def _blink_frame(self) -> None:
        self._blink_step += 1
        half = self._BLINK_STEPS
        total = half * 2
        if self._blink_step <= half:
            self._blink_phase = self._blink_step / half
        else:
            self._blink_phase = 1.0 - (self._blink_step - half) / half
        self._blink_phase = max(0.0, min(1.0, self._blink_phase))
        if self._blink_step >= total:
            self._blink_anim.stop()
            self._blink_phase = 0.0
            self._schedule_blink()

    # ── Eye Wander ────────────────────────────────────────────────────────

    def _wander(self) -> None:
        mult = self._current_eye_wander_mult
        activity = MascotActivity.IDLE
        if self._target_snapshot:
            activity = self._target_snapshot.activity

        if activity == MascotActivity.THINKING:
            self._eye_tx = random.uniform(2.2, 3.8) * mult
            self._eye_ty = random.uniform(-3.5, -1.8) * mult
        elif activity == MascotActivity.IDLE:
            self._eye_tx = random.uniform(-2.2, 2.2) * mult
            self._eye_ty = random.uniform(-1.2, 1.2) * mult
        self._wander_timer.start(random.randint(3000, 7500))

    # ── Paint Event ───────────────────────────────────────────────────────

    def paintEvent(self, _event) -> None:
        w = float(self.width())
        h = float(self.height())
        t = self._t

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Procedural breathing
        b_speed = 2.05 * self._current_breathe_speed_mult
        float_y = math.sin(t * 0.85) * 7.0 * self._current_breathe_amp * (h / 420.0)
        b_scale = 1.0 + math.sin(t * b_speed) * 0.013 * self._current_breathe_amp

        p.save()
        p.translate(0.0, float_y)

        self._paint_aura(p, w, h, t)
        self._paint_torso(p, w, h, t, b_scale)
        self._paint_neck(p, w, h, t)

        # Head section with tilt rotation
        self._paint_head(p, w, h, t, self._current_head_tilt)

        p.restore()

        # Eye pulse overlays
        self._paint_eye_pulse(p, w, h, t, float_y)

        p.end()

    # ── Render Layers ─────────────────────────────────────────────────────

    def _paint_aura(self, p: QPainter, w: float, h: float, t: float) -> None:
        r = (w * 0.52) * (1.0 + math.sin(t * 1.4) * 0.025)
        cx = w * 0.5
        cy = h * 0.40
        g = QRadialGradient(cx, cy, r)
        
        c = self._current_primary_accent
        g.setColorAt(0.00, QColor(c.red() // 3, c.green() // 3, c.blue() // 2, 48))
        g.setColorAt(0.45, QColor(c.red() // 4, c.green() // 4, c.blue() // 3, 22))
        g.setColorAt(1.00, QColor(11, 18, 35, 0))
        
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QRectF(cx - r, cy - r, r * 2.0, r * 2.0))

    def _paint_torso(self, p: QPainter, w: float, h: float, t: float, b_scale: float) -> None:
        p.save()
        p.translate(w * 0.5, h)
        p.scale(1.0, b_scale)
        p.translate(-w * 0.5, -h)

        sy = h / 420.0
        sx = w / 320.0

        # Torso base
        chest = QPainterPath()
        chest.moveTo(w * 0.24, h)
        chest.cubicTo(w * 0.24, 395.0 * sy, w * 0.39, 352.0 * sy, w * 0.5, 352.0 * sy)
        chest.cubicTo(w * 0.61, 352.0 * sy, w * 0.76, 395.0 * sy, w * 0.76, h)
        chest.closeSubpath()

        cg = QLinearGradient(0, 352.0 * sy, 0, h)
        cg.setColorAt(0.0, QColor(30, 34, 55))
        cg.setColorAt(1.0, QColor(12, 14, 22))
        p.setBrush(QBrush(cg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(chest)

        # Glass shoulder mantle
        mantle = QPainterPath()
        mantle.moveTo(w * 0.13, h)
        mantle.cubicTo(w * 0.13, 375.0 * sy, w * 0.32, 326.0 * sy, w * 0.5, 326.0 * sy)
        mantle.cubicTo(w * 0.68, 326.0 * sy, w * 0.87, 375.0 * sy, w * 0.87, h)
        mantle.closeSubpath()

        mg = QLinearGradient(w * 0.13, 326.0 * sy, w * 0.87, h)
        mg.setColorAt(0.0, QColor(255, 255, 255, 32))
        mg.setColorAt(1.0, QColor(255, 255, 255, 6))
        p.setBrush(QBrush(mg))
        p.drawPath(mantle)

        p.setPen(QPen(QColor(255, 255, 255, 45), 1.5 * sx))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(mantle)

        # Torso side glow seams
        seam_l = QPainterPath()
        seam_l.moveTo(w * 0.22, h)
        seam_l.cubicTo(w * 0.22, 392.0 * sy, w * 0.37, 354.0 * sy, w * 0.5, 354.0 * sy)

        seam_r = QPainterPath()
        seam_r.moveTo(w * 0.5, 354.0 * sy)
        seam_r.cubicTo(w * 0.63, 354.0 * sy, w * 0.78, 392.0 * sy, w * 0.78, h)

        c_prim = self._current_primary_accent
        c_sec = self._current_secondary_accent

        for seam in (seam_l, seam_r):
            # Outer bloom
            p.setPen(QPen(QColor(c_prim.red(), c_prim.green(), c_prim.blue(), 18), 10.0 * sx,
                          Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawPath(seam)
            
            # Core seam line
            sg = QLinearGradient(w * 0.22, 354.0 * sy, w * 0.5, h)
            sg.setColorAt(0.0, QColor(c_prim.red(), c_prim.green(), c_prim.blue(), 0))
            sg.setColorAt(0.35, QColor(c_prim.red(), c_prim.green(), c_prim.blue(), 210))
            sg.setColorAt(0.65, QColor(c_sec.red(), c_sec.green(), c_sec.blue(), 210))
            sg.setColorAt(1.0, QColor(c_prim.red() // 2, c_prim.green() // 2, c_prim.blue() // 2, 180))
            p.setPen(QPen(QBrush(sg), 2.4 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawPath(seam)

        p.restore()

    def _paint_neck(self, p: QPainter, w: float, h: float, t: float) -> None:
        sy = h / 420.0
        sx = w / 320.0

        ring_cx = w * 0.5
        ring_cy = 314.0 * sy
        ring_rx = 40.0 * sx
        ring_ry = 11.0 * sy
        pulse = int(155 + 55 * math.sin(t * 3.2))

        c_prim = self._current_primary_accent
        c_pulse = self._current_pulse_color

        # Outer bloom ring
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(c_prim.red(), c_prim.green(), c_prim.blue(), pulse // 4))
        p.drawEllipse(QRectF(ring_cx - ring_rx * 1.65, ring_cy - ring_ry * 1.65,
                             ring_rx * 3.3, ring_ry * 3.3))
        # Solid center ring
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(c_prim.red(), c_prim.green(), c_prim.blue(), pulse))
        p.drawEllipse(QRectF(ring_cx - ring_rx, ring_cy - ring_ry,
                             ring_rx * 2.0, ring_ry * 2.0))
        
        # Neck (tapered)
        neck = QPainterPath()
        neck.moveTo(124.0 * sx, 268.0 * sy)
        neck.quadTo(w * 0.5, 280.0 * sy, w - 124.0 * sx, 268.0 * sy)
        neck.lineTo(w - 124.0 * sx, 320.0 * sy)
        neck.quadTo(w * 0.5, 335.0 * sy, 124.0 * sx, 320.0 * sy)
        neck.closeSubpath()

        ng = QLinearGradient(w * 0.5, 268.0 * sy, w * 0.5, 320.0 * sy)
        ng.setColorAt(0.0, QColor(14, 15, 20))
        ng.setColorAt(1.0, QColor(85, 100, 125))
        p.setBrush(QBrush(ng))
        p.drawPath(neck)

        # Soft cast shadow on neck
        lshadow = QPainterPath()
        lshadow.moveTo(124.0 * sx, 268.0 * sy)
        lshadow.cubicTo(124.0 * sx, 268.0 * sy,
                        126.0 * sx, 296.0 * sy,
                        132.0 * sx, 320.0 * sy)
        lshadow.lineTo(142.0 * sx, 268.0 * sy)
        p.setBrush(QColor(96, 126, 158, 60))
        p.drawPath(lshadow)

        # Right rim light edge on neck
        p.setPen(QPen(QColor(c_prim.red(), c_prim.green(), c_prim.blue(), 50), 3.5 * sx,
                      Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        rim_p = QPainterPath()
        rim_p.moveTo(w - 132.0 * sx, 268.0 * sy)
        rim_p.cubicTo(w - 126.0 * sx, 278.0 * sy,
                      w - 128.0 * sx, 298.0 * sy,
                      w - 136.0 * sx, 320.0 * sy)
        p.drawPath(rim_p)
        
        # Neck muscle and Adam's Apple details
        neck_lines = QPainterPath()
        neck_lines.moveTo(133.0 * sx, 280.0 * sy)
        neck_lines.quadTo(140.0 * sx, 300.0 * sy, 145.0 * sx, 320.0 * sy)
        neck_lines.moveTo(187.0 * sx, 280.0 * sy)
        neck_lines.quadTo(180.0 * sx, 300.0 * sy, 175.0 * sx, 320.0 * sy)
        # Adam's Apple
        neck_lines.moveTo(153.0 * sx, 298.0 * sy)
        neck_lines.lineTo(160.0 * sx, 308.0 * sy)
        neck_lines.lineTo(167.0 * sx, 298.0 * sy)
        p.setPen(QPen(QColor(30, 35, 50, 110), 2.5 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(neck_lines)   

        # Inner highlight ring
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(c_pulse.red(), c_pulse.green(), c_pulse.blue(), pulse // 2))
        p.drawEllipse(QRectF(ring_cx - ring_rx * 0.7, ring_cy - ring_ry * 0.6,
                             ring_rx * 1.4, ring_ry * 0.6))

    def _paint_head(self, p: QPainter, w: float, h: float, t: float, tilt: float) -> None:
        p.save()
        cx, cy = w * 0.5, h * 0.39
        p.translate(cx, cy)
        p.rotate(tilt)
        p.translate(-cx, -cy)

        sy = h / 420.0
        sx = w / 320.0

        # Exact hair mass from SVG
        hair = QPainterPath()
        hair.moveTo(82.0 * sx, 185.0 * sy)
        hair.quadTo(80.0 * sx, 130.0 * sy, 98.0 * sx, 105.0 * sy)
        hair.quadTo(122.0 * sx, 68.0 * sy, 160.0 * sx, 68.0 * sy)
        hair.quadTo(198.0 * sx, 68.0 * sy, 222.0 * sx, 105.0 * sy)
        hair.quadTo(240.0 * sx, 130.0 * sy, 238.0 * sx, 185.0 * sy)
        hair.lineTo(232.0 * sx, 155.0 * sy)
        hair.lineTo(224.0 * sx, 158.0 * sy)
        hair.quadTo(216.0 * sx, 130.0 * sy, 190.0 * sx, 92.0 * sy)
        hair.quadTo(160.0 * sx, 92.0 * sy, 130.0 * sx, 92.0 * sy)
        hair.quadTo(104.0 * sx, 130.0 * sy, 96.0 * sx, 158.0 * sy)
        hair.lineTo(88.0 * sx, 155.0 * sy)
        hair.closeSubpath()

        hg = QLinearGradient(0, 55.0 * sy, 0, 272.0 * sy)
        hg.setColorAt(0.0, QColor(26, 28, 44))
        hg.setColorAt(1.0, QColor(12, 14, 22))
        p.setBrush(QBrush(hg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(hair)

        # Hair sheen strip
        sheen_g = QLinearGradient(130.0 * sx, 62.0 * sy, 190.0 * sx, 72.0 * sy)
        sheen_g.setColorAt(0.0, QColor(40, 46, 72, 0))
        sheen_g.setColorAt(0.5, QColor(52, 58, 90, 130))
        sheen_g.setColorAt(1.0, QColor(40, 46, 72, 0))
        sheen = QPainterPath()
        sheen.moveTo(130.0 * sx, 66.0 * sy)
        sheen.cubicTo(148.0 * sx, 58.0 * sy, 175.0 * sx, 56.0 * sy, 200.0 * sx, 60.0 * sy)
        sheen.cubicTo(175.0 * sx, 64.0 * sy, 148.0 * sx, 66.0 * sy, 130.0 * sx, 66.0 * sy)
        p.setBrush(QBrush(sheen_g))
        p.drawPath(sheen)

        # Realistic masculine oval face shape
        face = QPainterPath()
        face.moveTo(85.0 * sx, 165.0 * sy)
        
        # Smooth forehead (width 150)
        face.cubicTo(85.0 * sx, 95.0 * sy, 115.0 * sx, 75.0 * sy, 160.0 * sx, 75.0 * sy)
        face.cubicTo(205.0 * sx, 75.0 * sy, 235.0 * sx, 95.0 * sy, 235.0 * sx, 165.0 * sy)
        
        # Right cheek dropping to jaw angle
        face.cubicTo(235.0 * sx, 215.0 * sy, 225.0 * sx, 255.0 * sy, 190.0 * sx, 280.0 * sy)
        
        # Right chin to center
        face.cubicTo(180.0 * sx, 290.0 * sy, 170.0 * sx, 295.0 * sy, 160.0 * sx, 295.0 * sy)
        
        # Center to left chin
        face.cubicTo(150.0 * sx, 295.0 * sy, 140.0 * sx, 290.0 * sy, 130.0 * sx, 280.0 * sy)
        
        # Left jaw angle to cheek
        face.cubicTo(95.0 * sx, 255.0 * sy, 85.0 * sx, 215.0 * sy, 85.0 * sx, 165.0 * sy)
        
        face.closeSubpath()

        # Face core light/shadow gradients
        fg = QLinearGradient(120.0 * sx, 73.0 * sy, w - 120.0 * sx, 276.0 * sy)
        fg.setColorAt(0.0,  QColor(238, 245, 252))
        fg.setColorAt(0.35, QColor(205, 222, 238))
        fg.setColorAt(0.85, QColor(170, 185, 215))
        fg.setColorAt(1.0,  QColor(135, 145, 175))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(fg))
        p.drawPath(face)

        # Facial Contours (Cheek hollow shadows)
        hollows = QPainterPath()
        hollows.moveTo(95.0 * sx, 195.0 * sy)
        hollows.quadTo(110.0 * sx, 230.0 * sy, 120.0 * sx, 255.0 * sy)
        hollows.moveTo(225.0 * sx, 195.0 * sy)
        hollows.quadTo(210.0 * sx, 230.0 * sy, 200.0 * sx, 255.0 * sy)
        p.setPen(QPen(QColor(110, 125, 150, 45), 7.0 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(hollows)

        # Realistic Volumetric Skin Shading (Multi-stroke blur technique)
        p.setBrush(Qt.BrushStyle.NoBrush)
        
        folds = QPainterPath()
        
        # Under-eye fatigue lines
        folds.moveTo(92.0 * sx, 193.0 * sy)
        folds.cubicTo(102.0 * sx, 203.0 * sy, 118.0 * sx, 203.0 * sy, 126.0 * sx, 193.0 * sy)
        folds.moveTo(228.0 * sx, 193.0 * sy)
        folds.cubicTo(218.0 * sx, 203.0 * sy, 202.0 * sx, 203.0 * sy, 194.0 * sx, 193.0 * sy)
        
        # Nasolabial folds (Smile lines)
        folds.moveTo(146.0 * sx, 202.0 * sy)
        folds.cubicTo(138.0 * sx, 212.0 * sy, 131.0 * sx, 230.0 * sy, 135.0 * sx, 255.0 * sy)
        folds.moveTo(174.0 * sx, 202.0 * sy)
        folds.cubicTo(182.0 * sx, 212.0 * sy, 189.0 * sx, 230.0 * sy, 185.0 * sx, 255.0 * sy)
        
        # Soft Shadow Layers
        shadow_widths = [8.0, 5.0, 2.5, 1.0]
        shadow_alphas = [5, 10, 18, 25]
        for width_sx, alpha in zip(shadow_widths, shadow_alphas):
            p.setPen(QPen(QColor(110, 125, 155, alpha), width_sx * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawPath(folds)
            
        # Soft Highlight Layers (creates the 3D skin fold volume)
        p.translate(0, 1.5 * sy)
        highlight_widths = [6.0, 3.0, 1.2]
        highlight_alphas = [8, 15, 25]
        for width_sx, alpha in zip(highlight_widths, highlight_alphas):
            p.setPen(QPen(QColor(245, 250, 255, alpha), width_sx * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawPath(folds)
        p.translate(0, -1.5 * sy)

        # Face Key light highlights (cool radial gloss)
        kg = QRadialGradient(w * 0.30, h * 0.20, w * 0.38)
        kg.setColorAt(0.0, QColor(245, 252, 255, 95))
        kg.setColorAt(0.5, QColor(220, 238, 252, 40))
        kg.setColorAt(1.0, QColor(200, 220, 240, 0))
        p.setBrush(QBrush(kg))
        p.drawPath(face)

        # Rim light (blue/colored side glow)
        c_prim = self._current_primary_accent
        rg = QLinearGradient(w * 0.62, 0, w, 0)
        rg.setColorAt(0.0, QColor(c_prim.red() // 2, c_prim.green() // 2, c_prim.blue() // 2, 0))
        rg.setColorAt(0.7, QColor(c_prim.red() // 2, c_prim.green() // 2, c_prim.blue() // 2, 24))
        rg.setColorAt(1.0, QColor(c_prim.red(), c_prim.green(), c_prim.blue(), 48))
        p.setBrush(QBrush(rg))
        p.drawPath(face)


        # Face features & temple trace layers
        self._paint_features(p, w, h, sx, sy)
        self._paint_circuits(p, w, h, sx, sy)

        p.restore()

    def _paint_features(self, p: QPainter, w: float, h: float, sx: float, sy: float) -> None:
        glow        = self._current_glow_intensity
        raise_amt   = self._current_brow_raise
        furrow_amt  = self._current_brow_furrow
        mouth_curve = self._current_mouth_curve
        
        # Open mouth combined with speak phase lip-sync
        mouth_open = self._current_mouth_open
        activity = MascotActivity.IDLE
        if self._target_snapshot:
            activity = self._target_snapshot.activity
            
        if activity == MascotActivity.SPEAKING:
            sm = abs(math.sin(self._speak_phase)) * 0.48
            mouth_open = max(mouth_open, sm)
            mouth_curve = 0.35 + sm * 0.18

        # Eye alignments
        left_ex  = w * 0.382
        right_ex = w * 0.618
        eye_y    = h * 0.410
        brow_y   = eye_y - h * 0.063

        sclera_rx = w * 0.063
        sclera_ry = h * 0.037

        iris_r  = min(sclera_rx, sclera_ry) * 0.93
        pupil_r = iris_r * 0.50

        # Eyebrow offsets
        dy = -raise_amt * 8.0 * sy
        dx_in = furrow_amt * 4.5 * sx
        brow_half = sclera_rx * 1.08

        shadow_pen = QPen(QColor(18, 20, 32), 7.8 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        main_pen   = QPen(QColor(26, 28, 46), 4.5 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        hi_pen     = QPen(QColor(52, 58, 82, 145), 1.6 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)

        for (ex, mirror) in ((left_ex, 1.0), (right_ex, -1.0)):
            emotion = MascotEmotion.NEUTRAL
            if self._target_snapshot:
                emotion = self._target_snapshot.emotion
                
            curious_dy = -6.0 * sy if (emotion == MascotEmotion.CURIOUS and mirror == 1.0) else 0.0
            
            # Dynamic vertical positions for the brow shape
            inner_y = brow_y + furrow_amt * 12.0 * sy
            outer_y = brow_y - raise_amt * 6.0 * sy
            
            # Base geometry with dynamic furrow (dx_in) and raise (dy)
            inner_x = ex + 25.0 * sx * mirror - dx_in * 1.5 * mirror
            peak_x = ex - 12.0 * sx * mirror   # Arch peak
            outer_x = ex - 28.0 * sx * mirror  # Outer tail brought inward
            
            # Realistic Masculine Eyebrows (Strong angled arch, slightly lowered)
            brow = QPainterPath()
            brow.moveTo(inner_x, inner_y + curious_dy)
            # Bottom edge arches up to the peak
            brow.quadTo(ex, brow_y - 1.0 * sy + dy, peak_x, brow_y - 2.0 * sy + dy + curious_dy)
            # Then slopes down to the tail
            brow.quadTo(peak_x - 8.0 * sx * mirror, brow_y - 1.0 * sy + dy, outer_x, outer_y + curious_dy)
            # Top edge tapers from tail back up to the peak
            brow.quadTo(peak_x - 8.0 * sx * mirror, brow_y - 6.0 * sy + dy, peak_x, brow_y - 10.0 * sy + dy + curious_dy)
            # Then drops back down to the inner corner
            brow.quadTo(ex, brow_y - 6.0 * sy + dy, inner_x - 3.0 * sx * mirror, inner_y - 6.0 * sy + curious_dy)
            brow.closeSubpath()
            
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(18, 20, 30))
            p.drawPath(brow)

        # Frown creases (Confused / Sad / Concerned)
        if emotion in (MascotEmotion.CONFUSED, MascotEmotion.SAD, MascotEmotion.CONCERNED, MascotEmotion.ANGRY):
            cp = QPen(QColor(140, 166, 195, 52), 0.9 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(cp)
            for i in range(2):
                cy2 = brow_y - (14 + i * 5) * sy
                cr  = QPainterPath()
                cr.moveTo(w * 0.5 - 15.0 * sx, cy2)
                cr.quadTo(w * 0.5, cy2 - 2.5 * sy, w * 0.5 + 15.0 * sx, cy2)
                p.drawPath(cr)

        # Sclera (White eye background) and Blink Animation
        blink = self._blink_phase
        p.setPen(Qt.PenStyle.NoPen)
        
        sclera_path_full = QPainterPath()
        for ex in (left_ex, right_ex):
            # Dynamic blinking curve (open_ry goes from +sclera_ry down to -sclera_ry)
            open_ry = sclera_ry * (1.0 - blink * 2.0)
            
            almond = QPainterPath()
            almond.moveTo(ex - sclera_rx, eye_y)
            almond.quadTo(ex, eye_y - open_ry, ex + sclera_rx, eye_y)
            almond.quadTo(ex, eye_y + sclera_ry, ex - sclera_rx, eye_y)
            sclera_path_full.addPath(almond)

            sclera_g = QRadialGradient(ex - sclera_rx * 0.2, eye_y - sclera_ry * 0.3, sclera_rx * 1.4)
            sclera_g.setColorAt(0.0, QColor(244, 250, 255))
            sclera_g.setColorAt(0.6, QColor(230, 242, 252))
            sclera_g.setColorAt(1.0, QColor(208, 226, 242))
            p.setBrush(QBrush(sclera_g))
            p.drawPath(almond)

            # Cast shadow from eyelids
            ets = QLinearGradient(ex, eye_y - sclera_ry, ex, eye_y)
            ets.setColorAt(0.0, QColor(160, 192, 218, 95))
            ets.setColorAt(0.7, QColor(160, 192, 218, 0))
            p.setBrush(QBrush(ets))
            p.drawPath(almond)

            p.setBrush(QColor(210, 155, 165, 70))
            p.drawEllipse(QRectF(ex - sclera_rx - 3.0 * sx, eye_y - 3.0 * sy, 7.0 * sx, 6.0 * sy))

        # Set clipping path so Iris and Catchlights never draw outside the eye socket!
        p.save()
        p.setClipPath(sclera_path_full)

        # Iris + Pupil
        ox = self._eye_ox * sx
        oy = self._eye_oy * sy
        c_prim = self._current_primary_accent
        c_sec = self._current_secondary_accent

        for ex in (left_ex, right_ex):
            px, py = ex + ox, eye_y + oy
            max_m  = iris_r * 0.32
            dist   = math.hypot(px - ex, py - eye_y)
            if dist > max_m:
                ang = math.atan2(py - eye_y, px - ex)
                px  = ex  + math.cos(ang) * max_m
                py  = eye_y + math.sin(ang) * max_m

            # Natural Human Eye Color (Deep Amber / Hazel)
            base_color = QColor(60, 45, 20)    # Deep brown base
            mid_color = QColor(110, 80, 35)    # Warm hazel
            light_color = QColor(160, 120, 50) # Amber highlight
            dark_edge = QColor(25, 15, 5)      # Very dark outer ring
            
            ig = QRadialGradient(px - iris_r * 0.22, py - iris_r * 0.28, iris_r)
            ig.setColorAt(0.00, light_color)
            ig.setColorAt(0.30, mid_color)
            ig.setColorAt(0.70, base_color)
            ig.setColorAt(1.00, dark_edge)
            
            p.setBrush(QBrush(ig))
            p.drawEllipse(QRectF(px - iris_r, py - iris_r, iris_r * 2.0, iris_r * 2.0))

            # Pupil size with dynamic breathing dilation
            dyn_pupil_r = pupil_r * (1.0 + 0.06 * math.sin(self._t * 1.8))

            # Pupil core
            pg = QRadialGradient(px - dyn_pupil_r * 0.18, py - dyn_pupil_r * 0.18, dyn_pupil_r)
            pg.setColorAt(0.0, QColor(16, 14, 28))
            pg.setColorAt(1.0, QColor(4, 4, 10))
            p.setBrush(QBrush(pg))
            p.drawEllipse(QRectF(px - dyn_pupil_r, py - dyn_pupil_r, dyn_pupil_r * 2.0, dyn_pupil_r * 2.0))

            # Single soft, natural catchlight (environment reflection)
            cl_r = pupil_r * 0.40
            p.setBrush(QColor(255, 255, 255, 210))
            p.drawEllipse(QRectF(px - pupil_r * 0.42 - cl_r, py - pupil_r * 0.52 - cl_r, cl_r * 2.0, cl_r * 2.0))

        # Remove the clipping path so eyelashes can draw on top of the skin
        p.restore()
        
        # Realistic Eyelids and Eyelashes (Animated dynamically with blink)
        for (ex, mirror) in ((left_ex, 1.0), (right_ex, -1.0)):
            x_out = ex - sclera_rx * mirror
            x_in  = ex + sclera_rx * mirror
            
            p.save()
            # Rotate on its axis! (Simulated 3D pitch rotation via Y-scaling)
            # This perfectly flips the eyelid convex shape down over the sphere!
            scale_y = 1.0 - 2.0 * blink
            p.translate(ex, eye_y)
            p.scale(1.0, scale_y)
            p.translate(-ex, -eye_y)
            
            # Tapered solid masculine eyelash (Static geometry, animated by transform)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(18, 20, 30))
            lash = QPainterPath()
            # Start at inner duct
            lash.moveTo(x_in, eye_y)
            # Bottom curve (perfectly hugging the convex round eye socket)
            lash.quadTo(ex, eye_y - sclera_ry * 1.3, x_out, eye_y)
            # Soft rounded taper at outer edge
            lash.quadTo(x_out - 1.5 * sx * mirror, eye_y - 1.5 * sy, x_out - 1.0 * sx * mirror, eye_y - 2.5 * sy)
            # Top convex curve (giving natural thickness)
            lash.quadTo(ex, eye_y - sclera_ry * 1.7, x_in, eye_y - 0.5 * sy)
            lash.closeSubpath()
            p.drawPath(lash)
            
            p.setBrush(Qt.BrushStyle.NoBrush)
            
            # Upper Eyelid Crease (skin fold above the eye)
            crease = QPainterPath()
            crease.moveTo(x_in - 2.0 * sx * mirror, eye_y - 2.0 * sy)
            crease.quadTo(ex, eye_y - sclera_ry * 2.2, x_out - 2.0 * sx * mirror, eye_y - 1.0 * sy)
            
            p.setPen(QPen(QColor(105, 120, 145, 110), 1.5 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawPath(crease)
            p.translate(0, 1.0 * sy)
            p.setPen(QPen(QColor(255, 255, 255, 30), 1.0 * sx))
            p.drawPath(crease)
            
            p.restore()
            
            # Lower eyelid waterline & shadow (static)
            lower_lid = QPainterPath()
            lower_lid.moveTo(x_out + 4.0 * sx * mirror, eye_y + 1.5 * sy)
            lower_lid.quadTo(ex, eye_y + sclera_ry * 1.25, x_in - 3.0 * sx * mirror, eye_y + 1.0 * sy)
            
            p.setPen(QPen(QColor(230, 240, 255, 60), 1.1 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawPath(lower_lid)
            p.translate(0, 1.2 * sy)
            p.setPen(QPen(QColor(115, 130, 150, 80), 1.2 * sx))
            p.drawPath(lower_lid)
            p.translate(0, -1.2 * sy)

        # Realistic Volumetric Nose
        nose_cx = w * 0.5
        nose_bottom_y = h * 0.53  # Lengthened nose
        
        # 1. Nose bottom cast shadow (depth under the tip)
        p.setPen(Qt.PenStyle.NoPen)
        ng_shadow = QRadialGradient(nose_cx, nose_bottom_y + 4.0 * sy, 14.0 * sx)
        ng_shadow.setColorAt(0.0, QColor(105, 120, 145, 55))
        ng_shadow.setColorAt(1.0, QColor(105, 120, 145, 0))
        p.setBrush(QBrush(ng_shadow))
        p.drawEllipse(QRectF(nose_cx - 16.0 * sx, nose_bottom_y - 2.0 * sy, 32.0 * sx, 20.0 * sy))
        
        # 2. Nose bridge side shadows (connects inner eyebrows down to tip)
        bridge_shadow = QPainterPath()
        bridge_shadow.moveTo(nose_cx - 12.0 * sx, h * 0.38) # Near left eye
        bridge_shadow.quadTo(nose_cx - 6.0 * sx, h * 0.46, nose_cx - 10.0 * sx, nose_bottom_y - 4.0 * sy)
        bridge_shadow.moveTo(nose_cx + 12.0 * sx, h * 0.38) # Near right eye
        bridge_shadow.quadTo(nose_cx + 6.0 * sx, h * 0.46, nose_cx + 10.0 * sx, nose_bottom_y - 4.0 * sy)
        
        p.setPen(QPen(QColor(110, 125, 155, 30), 6.0 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(bridge_shadow)
        
        # 3. Nose tip bulb highlight (volumetric gloss)
        ng_bulb = QRadialGradient(nose_cx, nose_bottom_y - 4.0 * sy, 10.0 * sx)
        ng_bulb.setColorAt(0.0, QColor(245, 250, 255, 60))
        ng_bulb.setColorAt(1.0, QColor(245, 250, 255, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(ng_bulb))
        p.drawEllipse(QRectF(nose_cx - 12.0 * sx, nose_bottom_y - 12.0 * sy, 24.0 * sx, 18.0 * sy))
        
        # 4. Alar wings (outer nostril creases)
        wings = QPainterPath()
        wings.moveTo(nose_cx - 14.0 * sx, nose_bottom_y - 5.0 * sy)
        wings.quadTo(nose_cx - 19.0 * sx, nose_bottom_y + 3.0 * sy, nose_cx - 8.0 * sx, nose_bottom_y + 3.0 * sy)
        
        wings.moveTo(nose_cx + 14.0 * sx, nose_bottom_y - 5.0 * sy)
        wings.quadTo(nose_cx + 19.0 * sx, nose_bottom_y + 3.0 * sy, nose_cx + 8.0 * sx, nose_bottom_y + 3.0 * sy)
        
        p.setPen(QPen(QColor(115, 130, 155, 90), 1.8 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(wings)
        
        # 5. Nostril holes (inner cavities)
        holes = QPainterPath()
        holes.moveTo(nose_cx - 9.5 * sx, nose_bottom_y)
        holes.quadTo(nose_cx - 5.0 * sx, nose_bottom_y - 4.0 * sy, nose_cx - 3.0 * sx, nose_bottom_y + 1.5 * sy)
        
        holes.moveTo(nose_cx + 9.5 * sx, nose_bottom_y)
        holes.quadTo(nose_cx + 5.0 * sx, nose_bottom_y - 4.0 * sy, nose_cx + 3.0 * sx, nose_bottom_y + 1.5 * sy)
        
        p.setPen(QPen(QColor(60, 75, 95, 180), 2.2 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawPath(holes)

        # Mouth Lip outline and mouth opening
        mouth_cx = w * 0.5
        mouth_cy = h * 0.602
        mouth_hw = w * 0.075 # Slightly wider/longer mouth
        ctrl_y   = -mouth_curve * 12.0 * sy

        mouth_pen = QPen(_COL_MOUTH, 2.8 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(mouth_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)

        # Upper Lip with subtle Cupid's bow for enhanced lip shape
        upper = QPainterPath()
        upper.moveTo(mouth_cx - mouth_hw, mouth_cy)
        upper.cubicTo(mouth_cx - mouth_hw * 0.5, mouth_cy + ctrl_y - 1.5 * sy,
                      mouth_cx - mouth_hw * 0.1, mouth_cy + ctrl_y + 1.0 * sy,
                      mouth_cx, mouth_cy + ctrl_y + 1.5 * sy)
        upper.cubicTo(mouth_cx + mouth_hw * 0.1, mouth_cy + ctrl_y + 1.0 * sy,
                      mouth_cx + mouth_hw * 0.5, mouth_cy + ctrl_y - 1.5 * sy,
                      mouth_cx + mouth_hw, mouth_cy)
        p.drawPath(upper)

        open_h = max(0.0, mouth_open) * 15.0 * sy

        if mouth_open > 0.06:
            # Inner mouth dark cavity
            inner = QPainterPath()
            inner.moveTo(mouth_cx - mouth_hw * 0.83, mouth_cy)
            inner.quadTo(mouth_cx, mouth_cy + ctrl_y, mouth_cx + mouth_hw * 0.83, mouth_cy)
            inner.quadTo(mouth_cx + mouth_hw * 0.55, mouth_cy + open_h, mouth_cx, mouth_cy + open_h + 2.5 * sy)
            inner.quadTo(mouth_cx - mouth_hw * 0.55, mouth_cy + open_h, mouth_cx - mouth_hw * 0.83, mouth_cy)
            p.setBrush(QColor(16, 10, 20))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawPath(inner)

            # Upper teeth: a sleek white curved band at the top of the oral cavity
            teeth = QPainterPath()
            teeth.moveTo(mouth_cx - mouth_hw * 0.65, mouth_cy + ctrl_y + 0.5 * sy)
            teeth.quadTo(mouth_cx, mouth_cy + ctrl_y + 1.2 * sy, mouth_cx + mouth_hw * 0.65, mouth_cy + ctrl_y + 0.5 * sy)
            teeth.lineTo(mouth_cx + mouth_hw * 0.65, mouth_cy + ctrl_y + 3.0 * sy)
            teeth.quadTo(mouth_cx, mouth_cy + ctrl_y + 3.8 * sy, mouth_cx - mouth_hw * 0.65, mouth_cy + ctrl_y + 3.0 * sy)
            teeth.closeSubpath()
            p.setBrush(QColor(245, 248, 255))
            p.drawPath(teeth)

            # Lower tongue: soft warm pink gradient at the bottom of the oral cavity
            tongue = QPainterPath()
            tongue_y = mouth_cy + open_h - 4.0 * sy
            tongue.moveTo(mouth_cx - mouth_hw * 0.45, tongue_y)
            tongue.quadTo(mouth_cx, tongue_y - 2.5 * sy, mouth_cx + mouth_hw * 0.45, tongue_y)
            tongue.quadTo(mouth_cx + mouth_hw * 0.35, mouth_cy + open_h, mouth_cx, mouth_cy + open_h + 1.0 * sy)
            tongue.quadTo(mouth_cx - mouth_hw * 0.35, mouth_cy + open_h, mouth_cx - mouth_hw * 0.45, tongue_y)
            tongue.closeSubpath()
            tg = QRadialGradient(mouth_cx, mouth_cy + open_h, mouth_hw * 0.6)
            tg.setColorAt(0.0, QColor(220, 110, 130, 200))
            tg.setColorAt(1.0, QColor(140, 60, 80, 220))
            p.setBrush(QBrush(tg))
            p.drawPath(tongue)

            # Redraw upper lip border on top
            p.setPen(mouth_pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPath(upper)

        # Lower lip border (drawn whether mouth is open or closed)
        lower = QPainterPath()
        lower.moveTo(mouth_cx - mouth_hw * 0.85, mouth_cy)
        lower.quadTo(mouth_cx, mouth_cy + open_h + 4.5 * sy, mouth_cx + mouth_hw * 0.85, mouth_cy)
        p.setPen(QPen(_COL_MOUTH, 2.2 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(lower)
        
        # Cast shadow under the lower lip (creates 3D lip volume)
        lip_shadow = QPainterPath()
        lip_shadow.moveTo(mouth_cx - mouth_hw * 0.6, mouth_cy + open_h + 7.0 * sy)
        lip_shadow.quadTo(mouth_cx, mouth_cy + open_h + 12.0 * sy, mouth_cx + mouth_hw * 0.6, mouth_cy + open_h + 7.0 * sy)
        
        p.setPen(QPen(QColor(110, 125, 155, 30), 4.0 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawPath(lip_shadow)

        # Philtrum
        p.setPen(QPen(QColor(185, 160, 172, 88), 0.85 * sx))
        pf = QPainterPath()
        pf.moveTo(mouth_cx - 7.0 * sx, mouth_cy - 11.0 * sy)
        pf.quadTo(mouth_cx, mouth_cy - 16.0 * sy, mouth_cx + 7.0 * sx, mouth_cy - 11.0 * sy)
        p.drawPath(pf)

        # Dimple/Corners
        corner_pen = QPen(QColor(122, 95, 110, 145), 1.4 * sx, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(corner_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        for (ccx, sign) in ((mouth_cx - mouth_hw, -1.0), (mouth_cx + mouth_hw, 1.0)):
            cp = QPainterPath()
            cp.moveTo(ccx, mouth_cy)
            cp.quadTo(ccx - sign * 3.0 * sx, mouth_cy - 4.0 * sy, ccx - sign * 2.0 * sx, mouth_cy - 8.0 * sy)
            p.drawPath(cp)

    def _paint_circuits(self, p: QPainter, w: float, h: float, sx: float, sy: float) -> None:
        pass
    def _paint_eye_pulse(self, p: QPainter, w: float, h: float, t: float, float_y: float) -> None:
        emotion = MascotEmotion.NEUTRAL
        if self._target_snapshot:
            emotion = self._target_snapshot.emotion

        if emotion not in (MascotEmotion.HAPPY, MascotEmotion.CURIOUS, MascotEmotion.CONFUSED, MascotEmotion.SAD, MascotEmotion.CONCERNED):
            return

        glow = self._current_glow_intensity
        pulse = abs(math.sin(self._speak_phase * 0.55)) * 0.20 * glow
        if pulse < 0.008:
            return

        left_ex  = w * 0.382
        right_ex = w * 0.618
        eye_y    = h * 0.410 + float_y
        iris_r   = min(w * 0.073, h * 0.037) * 0.93

        # Disabled glowing cyan eye pulse to maintain natural human eyes
        pass

    # ── Size Hints ────────────────────────────────────────────────────────

    def sizeHint(self):
        from PySide6.QtCore import QSize
        return QSize(288, 380)

    def minimumSizeHint(self):
        from PySide6.QtCore import QSize
        return QSize(180, 238)
