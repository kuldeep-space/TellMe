"""
AnimationManager — centralized registry and factory for all UI animations.
"""
from PySide6.QtCore import QObject, QPropertyAnimation, QEasingCurve
from typing import Any
from frontend.engine.token_resolver import TokenResolver
from backend.core.logging import get_logger

_logger = get_logger(__name__)


class AnimationManager(QObject):
    """
    Creates and owns QPropertyAnimations for widgets.
    """
    def __init__(self, resolver: TokenResolver, parent: QObject | None = None):
        super().__init__(parent)
        self._resolver = resolver
        self._animations: dict[int, QPropertyAnimation] = {}
        self._reduce_motion = False
        self._global_speed = 1.0

    def set_reduce_motion(self, enabled: bool):
        self._reduce_motion = enabled
        if enabled:
            self.pause_all()
        else:
            self.resume_all()

    def set_global_speed(self, multiplier: float):
        self._global_speed = max(0.1, multiplier)

    def pause_all(self):
        for anim in self._animations.values():
            if anim.state() == QPropertyAnimation.State.Running:
                anim.pause()

    def resume_all(self):
        if self._reduce_motion:
            return
        for anim in self._animations.values():
            if anim.state() == QPropertyAnimation.State.Paused:
                anim.resume()

    def _get_duration(self, token_path: str) -> int:
        if self._reduce_motion:
            return 0
        base = self._resolver.resolve_int(token_path)
        return int(base / self._global_speed)

    def _get_easing(self, token_path: str) -> QEasingCurve.Type:
        val = self._resolver.resolve_int(token_path)
        return QEasingCurve.Type(val)

    def _make_anim(self, widget: QObject, prop: bytes, duration: int, easing: QEasingCurve.Type) -> QPropertyAnimation:
        anim = QPropertyAnimation(widget, prop, self)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve(easing))
        
        # Cleanup when widget dies
        widget.destroyed.connect(lambda obj: self._on_widget_destroyed(id(anim)))
        self._animations[id(anim)] = anim
        
        # Cleanup when animation finishes if it's not a loop
        anim.finished.connect(lambda: self._on_anim_finished(id(anim), anim))
        
        return anim

    def _on_widget_destroyed(self, anim_id: int):
        if anim_id in self._animations:
            anim = self._animations.pop(anim_id)
            try:
                anim.stop()
                anim.deleteLater()
            except RuntimeError:
                # The C++ object was already deleted by Qt
                pass

    def _on_anim_finished(self, anim_id: int, anim: QPropertyAnimation):
        # We don't remove it automatically because some animations are meant to be reused
        # (like hover lift that goes up and down). We only clear it if widget destroyed.
        pass
        
    def register_hover_lift(self, widget: Any, lift_px: int = 1) -> tuple[QPropertyAnimation, QPropertyAnimation]:
        """Returns (enter_anim, leave_anim) for manual triggering."""
        duration = self._get_duration("animation.duration_normal")
        easing = self._get_easing("animation.easing_out")
        
        enter = self._make_anim(widget, b"pos", duration, easing)
        leave = self._make_anim(widget, b"pos", duration, easing)
        
        # Caller is responsible for setting start/end values based on actual geometry at trigger time
        return enter, leave

    def register_press_depress(self, widget: Any, depress_px: int = 2) -> tuple[QPropertyAnimation, QPropertyAnimation]:
        duration_press = self._get_duration("animation.duration_fast")
        duration_release = self._get_duration("animation.duration_normal")
        easing_press = self._get_easing("animation.easing_out")
        easing_release = self._get_easing("animation.easing_spring")
        
        press = self._make_anim(widget, b"pos", duration_press, easing_press)
        release = self._make_anim(widget, b"pos", duration_release, easing_release)
        
        return press, release

    def register_led_pulse(self, widget: Any, alpha_property: bytes) -> QPropertyAnimation:
        period = self._resolver.resolve_int("animation.led_pulse_period_ms")
        if period == 0 or self._reduce_motion:
            # Dummy animation or none
            anim = QPropertyAnimation(widget, alpha_property, self)
            anim.setDuration(0)
            return anim
            
        duration = int(period / 2 / self._global_speed)
        anim = self._make_anim(widget, alpha_property, duration, QEasingCurve.Type.InOutSine)
        anim.setStartValue(1.0)
        anim.setEndValue(0.4)
        anim.setLoopCount(-1) # infinite
        anim.setDirection(QPropertyAnimation.Direction.Backward) # ping pong not directly supported without custom logic, but loop works if we reverse direction? Actually, for ping pong in Qt we can use KeyValueAt
        
        anim.setKeyValues([
            (0.0, 1.0),
            (0.5, 0.4),
            (1.0, 1.0)
        ])
        anim.setDuration(period)
        anim.start()
        
        return anim
