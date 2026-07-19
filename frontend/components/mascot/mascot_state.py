"""
MascotState — Decoupled, layered state configurations
for Emotion, Activity, and Presence dimensions.
"""
from enum import Enum, auto, IntEnum
from dataclasses import dataclass
from PySide6.QtGui import QColor


class MascotEmotion(Enum):
    NEUTRAL   = "neutral"
    HAPPY     = "happy"
    CURIOUS   = "curious"
    CONFUSED  = "confused"
    SAD       = "sad"
    CONCERNED = "concerned"
    ANGRY     = "angry"


class MascotActivity(Enum):
    IDLE      = "idle"
    LISTENING = "listening"
    THINKING  = "thinking"
    SPEAKING  = "speaking"


class MascotPresence(Enum):
    RELAXED   = "relaxed"
    FOCUSED   = "focused"
    ALERT     = "alert"
    ENGAGED   = "engaged"


class MascotEventType(Enum):
    SPEECH_STARTED    = auto()
    SPEECH_ENDED      = auto()
    THINKING_STARTED  = auto()
    AI_SPEECH_STARTED = auto()
    AI_SPEECH_ENDED   = auto()
    AI_TEXT_CHUNK     = auto()
    LOW_CONFIDENCE    = auto()
    EXPLICIT_EMOTION  = auto()


class EventPriority(IntEnum):
    LOW      = 10
    NORMAL   = 30
    HIGH     = 60
    CRITICAL = 100


@dataclass(frozen=True)
class EmotionConfig:
    """Internal parameters for visual emotion expressions."""
    mouth_curve: float
    brow_raise: float
    brow_furrow: float
    glow_intensity: float
    blink_rate: float
    
    # Timing
    enter_duration_ms: int
    hold_duration_ms: int
    exit_duration_ms: int

    # Theme colors
    primary_accent: QColor
    secondary_accent: QColor
    eye_glow: QColor
    pulse_color: QColor
    transition_speed: float  # Lerp coefficient (e.g. 0.08)


@dataclass(frozen=True)
class ActivityConfig:
    """Internal parameters for activity posture/focus."""
    head_tilt: float
    breathe_amp: float
    base_eye_x: float
    base_eye_y: float


@dataclass(frozen=True)
class PresenceConfig:
    """Internal parameters for presence variations."""
    breathe_speed_mult: float
    eye_wander_mult: float
    posture_mult: float


@dataclass(frozen=True)
class MascotSnapshot:
    """Immutable state containing only the resolved values for rendering."""
    emotion: MascotEmotion
    activity: MascotActivity
    presence: MascotPresence

    mouth_curve: float
    brow_raise: float
    brow_furrow: float
    mouth_open: float  # Set by controller/speaking activity

    head_tilt: float

    primary_accent: QColor
    secondary_accent: QColor
    eye_glow: QColor
    pulse_color: QColor

    glow_intensity: float
    blink_rate: float
    breathe_amp: float
    breathe_speed_mult: float

    eye_x_offset: float
    eye_y_offset: float
    eye_wander_mult: float

    transition_speed: float
    timestamp: float


# ── Color Themes (RGB values matching premium style guidelines) ─────────
_COLOR_BLUE_PRIMARY   = QColor(75, 150, 255)
_COLOR_BLUE_SECONDARY = QColor(130, 200, 255)
_COLOR_BLUE_GLOW      = QColor(75, 150, 255, 30)
_COLOR_BLUE_PULSE     = QColor(160, 210, 255, 120)

_COLOR_MINT_PRIMARY   = QColor(50, 210, 150)
_COLOR_MINT_SECONDARY = QColor(120, 255, 200)
_COLOR_MINT_GLOW      = QColor(50, 210, 150, 35)
_COLOR_MINT_PULSE     = QColor(120, 255, 200, 140)

_COLOR_AMBER_PRIMARY   = QColor(220, 180, 50)
_COLOR_AMBER_SECONDARY = QColor(255, 220, 100)
_COLOR_AMBER_GLOW      = QColor(220, 180, 50, 25)
_COLOR_AMBER_PULSE     = QColor(255, 220, 100, 110)

_COLOR_ORANGE_PRIMARY   = QColor(240, 130, 40)
_COLOR_ORANGE_SECONDARY = QColor(255, 180, 100)
_COLOR_ORANGE_GLOW      = QColor(240, 130, 40, 25)
_COLOR_ORANGE_PULSE     = QColor(255, 180, 100, 100)

_COLOR_CRIMSON_PRIMARY   = QColor(255, 75, 75)
_COLOR_CRIMSON_SECONDARY = QColor(255, 130, 130)
_COLOR_CRIMSON_GLOW      = QColor(255, 75, 75, 40)
_COLOR_CRIMSON_PULSE     = QColor(255, 130, 130, 150)

_COLOR_STEEL_PRIMARY   = QColor(115, 138, 178)
_COLOR_STEEL_SECONDARY = QColor(160, 185, 220)
_COLOR_STEEL_GLOW      = QColor(115, 138, 178, 15)
_COLOR_STEEL_PULSE     = QColor(160, 185, 220, 80)


# ── Configurations ───────────────────────────────────────────────────────

EMOTION_CONFIGS: dict[MascotEmotion, EmotionConfig] = {
    MascotEmotion.NEUTRAL: EmotionConfig(
        mouth_curve=0.3,
        brow_raise=0.0,
        brow_furrow=0.0,
        glow_intensity=1.0,
        blink_rate=1.0,
        enter_duration_ms=200,
        hold_duration_ms=500,
        exit_duration_ms=200,
        primary_accent=_COLOR_BLUE_PRIMARY,
        secondary_accent=_COLOR_BLUE_SECONDARY,
        eye_glow=_COLOR_BLUE_GLOW,
        pulse_color=_COLOR_BLUE_PULSE,
        transition_speed=0.08,
    ),
    MascotEmotion.HAPPY: EmotionConfig(
        mouth_curve=0.95,
        brow_raise=0.6,
        brow_furrow=0.0,
        glow_intensity=1.5,
        blink_rate=0.8,
        enter_duration_ms=250,
        hold_duration_ms=1500,
        exit_duration_ms=300,
        primary_accent=_COLOR_MINT_PRIMARY,
        secondary_accent=_COLOR_MINT_SECONDARY,
        eye_glow=_COLOR_MINT_GLOW,
        pulse_color=_COLOR_MINT_PULSE,
        transition_speed=0.06,
    ),
    MascotEmotion.CURIOUS: EmotionConfig(
        mouth_curve=0.2,
        brow_raise=0.6,
        brow_furrow=0.0,
        glow_intensity=1.1,
        blink_rate=0.8,
        enter_duration_ms=300,
        hold_duration_ms=1200,
        exit_duration_ms=300,
        primary_accent=_COLOR_AMBER_PRIMARY,
        secondary_accent=_COLOR_AMBER_SECONDARY,
        eye_glow=_COLOR_AMBER_GLOW,
        pulse_color=_COLOR_AMBER_PULSE,
        transition_speed=0.07,
    ),
    MascotEmotion.CONFUSED: EmotionConfig(
        mouth_curve=-0.1,
        brow_raise=0.2,
        brow_furrow=0.5,
        glow_intensity=0.9,
        blink_rate=1.3,
        enter_duration_ms=300,
        hold_duration_ms=1000,
        exit_duration_ms=300,
        primary_accent=_COLOR_AMBER_PRIMARY,
        secondary_accent=_COLOR_AMBER_SECONDARY,
        eye_glow=_COLOR_AMBER_GLOW,
        pulse_color=_COLOR_AMBER_PULSE,
        transition_speed=0.07,
    ),
    MascotEmotion.SAD: EmotionConfig(
        mouth_curve=-0.7,
        brow_raise=-0.1,
        brow_furrow=0.2,
        glow_intensity=0.7,
        blink_rate=0.7,
        enter_duration_ms=400,
        hold_duration_ms=1500,
        exit_duration_ms=400,
        primary_accent=_COLOR_STEEL_PRIMARY,
        secondary_accent=_COLOR_STEEL_SECONDARY,
        eye_glow=_COLOR_STEEL_GLOW,
        pulse_color=_COLOR_STEEL_PULSE,
        transition_speed=0.04,
    ),
    MascotEmotion.CONCERNED: EmotionConfig(
        mouth_curve=-0.4,
        brow_raise=0.1,
        brow_furrow=0.6,
        glow_intensity=0.8,
        blink_rate=0.9,
        enter_duration_ms=350,
        hold_duration_ms=1200,
        exit_duration_ms=350,
        primary_accent=_COLOR_ORANGE_PRIMARY,
        secondary_accent=_COLOR_ORANGE_SECONDARY,
        eye_glow=_COLOR_ORANGE_GLOW,
        pulse_color=_COLOR_ORANGE_PULSE,
        transition_speed=0.05,
    ),
    MascotEmotion.ANGRY: EmotionConfig(
        mouth_curve=-0.8,
        brow_raise=-0.5,
        brow_furrow=0.9,
        glow_intensity=1.2,
        blink_rate=0.6,
        enter_duration_ms=200,
        hold_duration_ms=1800,
        exit_duration_ms=350,
        primary_accent=_COLOR_CRIMSON_PRIMARY,
        secondary_accent=_COLOR_CRIMSON_SECONDARY,
        eye_glow=_COLOR_CRIMSON_GLOW,
        pulse_color=_COLOR_CRIMSON_PULSE,
        transition_speed=0.1,
    ),
}

ACTIVITY_CONFIGS: dict[MascotActivity, ActivityConfig] = {
    MascotActivity.IDLE: ActivityConfig(
        head_tilt=0.0,
        breathe_amp=1.0,
        base_eye_x=0.0,
        base_eye_y=0.0,
    ),
    MascotActivity.LISTENING: ActivityConfig(
        head_tilt=7.5,
        breathe_amp=0.7,
        base_eye_x=0.0,
        base_eye_y=0.0,
    ),
    MascotActivity.THINKING: ActivityConfig(
        head_tilt=0.0,
        breathe_amp=0.6,
        base_eye_x=-1.5,
        base_eye_y=-2.5,
    ),
    MascotActivity.SPEAKING: ActivityConfig(
        head_tilt=-1.0,
        breathe_amp=1.2,
        base_eye_x=0.0,
        base_eye_y=0.0,
    ),
}

PRESENCE_CONFIGS: dict[MascotPresence, PresenceConfig] = {
    MascotPresence.RELAXED: PresenceConfig(
        breathe_speed_mult=0.8,
        eye_wander_mult=0.6,
        posture_mult=0.7,
    ),
    MascotPresence.FOCUSED: PresenceConfig(
        breathe_speed_mult=1.0,
        eye_wander_mult=0.8,
        posture_mult=1.0,
    ),
    MascotPresence.ALERT: PresenceConfig(
        breathe_speed_mult=1.3,
        eye_wander_mult=1.5,
        posture_mult=1.2,
    ),
    MascotPresence.ENGAGED: PresenceConfig(
        breathe_speed_mult=1.0,
        eye_wander_mult=1.0,
        posture_mult=1.1,
    ),
}
