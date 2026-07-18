
from PySide6.QtCore import QEasingCurve

class AnimationTokens:
    # Easing Curves
    EASE_IN_OUT = QEasingCurve.Type.InOutSine
    EASE_OUT = QEasingCurve.Type.OutSine
    EASE_IN = QEasingCurve.Type.InSine
    SPRING = QEasingCurve.Type.OutBounce

