"""
MascotController — Event Queue, Priority, Emotion Resolving,
and Snapshot Generation for the AI Interviewer character.
"""
from __future__ import annotations
import heapq
import time
from typing import Optional, Union, Any

from PySide6.QtCore import QObject
from PySide6.QtGui import QColor

from frontend.components.mascot.mascot_state import (
    MascotEmotion, MascotActivity, MascotPresence, MascotEventType,
    EventPriority, MascotSnapshot, EMOTION_CONFIGS, ACTIVITY_CONFIGS,
    PRESENCE_CONFIGS
)


class MascotEvent:
    """A prioritized event received by the MascotController."""
    def __init__(
        self,
        event_type: MascotEventType,
        priority: EventPriority,
        timestamp: float,
        expiry_time_ms: float = 3000.0,
        payload: Optional[dict[str, Any]] = None
    ) -> None:
        self.event_type = event_type
        self.priority = priority
        self.timestamp = timestamp
        self.expiry_time_ms = expiry_time_ms
        self.payload = payload or {}

    def is_expired(self, current_time: float) -> bool:
        return (current_time - self.timestamp) * 1000.0 > self.expiry_time_ms


class MascotSignal:
    """Decoupled input data passed to the EmotionResolver."""
    def __init__(
        self,
        text: str = "",
        explicit: Optional[MascotEmotion] = None,
        vad_confidence: float = 1.0,
        asr_confidence: float = 1.0
    ) -> None:
        self.text = text
        self.explicit = explicit
        self.vad_confidence = vad_confidence
        self.asr_confidence = asr_confidence


class BaseEmotionResolver:
    """Interface for mapping MascotSignals to resolved MascotEmotions."""
    def resolve(self, signal: MascotSignal) -> MascotEmotion:
        raise NotImplementedError


class RuleBasedResolver(BaseEmotionResolver):
    """Rule and emoji-based emotion resolution."""
    def __init__(self) -> None:
        super().__init__()
        # Rules: list of (list of keywords, resolved emotion)
        self.rules: list[tuple[list[str], MascotEmotion]] = [
            (["great explanation", "excellent", "perfect", "good job", "wonderful", "correct", "well done"], MascotEmotion.HAPPY),
            (["explain that again", "could you clarify", "not sure", "unclear", "what do you mean", "why did you"], MascotEmotion.CONFUSED),
            (["unfortunately", "incorrect", "wrong", "not correct", "failed", "sorry"], MascotEmotion.SAD),
            (["how", "why", "what if", "tell me about", "describe"], MascotEmotion.CURIOUS),
        ]

        # Emoji mapping
        self.emojis: dict[str, MascotEmotion] = {
            "😊": MascotEmotion.HAPPY,
            "🙂": MascotEmotion.HAPPY,
            "😄": MascotEmotion.HAPPY,
            "😀": MascotEmotion.HAPPY,
            "👍": MascotEmotion.HAPPY,
            "🙌": MascotEmotion.HAPPY,
            "🤔": MascotEmotion.CURIOUS,
            "🧐": MascotEmotion.CURIOUS,
            "🤨": MascotEmotion.CURIOUS,
            "😕": MascotEmotion.CONFUSED,
            "❓": MascotEmotion.CONFUSED,
            "🤷": MascotEmotion.CONFUSED,
            "😮": MascotEmotion.CONFUSED,
            "😲": MascotEmotion.CONFUSED,
            "😢": MascotEmotion.SAD,
            "😭": MascotEmotion.SAD,
            "🙁": MascotEmotion.SAD,
            "☹️": MascotEmotion.SAD,
            "😠": MascotEmotion.ANGRY,
            "😡": MascotEmotion.ANGRY,
            "👿": MascotEmotion.ANGRY,
        }

    def resolve(self, signal: MascotSignal) -> MascotEmotion:
        # 1. Explicit override metadata takes precedence
        if signal.explicit is not None:
            return signal.explicit

        # 2. Check emojis
        for char, emotion in self.emojis.items():
            if char in signal.text:
                return emotion

        # 3. Rule-based sentiment matching
        text_lower = signal.text.lower()
        for keywords, emotion in self.rules:
            for kw in keywords:
                if kw in text_lower:
                    return emotion

        # 4. Fallback: Neutral
        return MascotEmotion.NEUTRAL


# ── Transition Routing Graph ─────────────────────────────────────────────
# Limits drastic leaps by routing through neutral or intermediate states
EMOTION_ROUTING: dict[tuple[MascotEmotion, MascotEmotion], MascotEmotion] = {
    (MascotEmotion.HAPPY,     MascotEmotion.ANGRY):     MascotEmotion.NEUTRAL,
    (MascotEmotion.HAPPY,     MascotEmotion.SAD):       MascotEmotion.NEUTRAL,
    (MascotEmotion.HAPPY,     MascotEmotion.CONCERNED): MascotEmotion.NEUTRAL,
    (MascotEmotion.ANGRY,     MascotEmotion.HAPPY):     MascotEmotion.NEUTRAL,
    (MascotEmotion.ANGRY,     MascotEmotion.SAD):       MascotEmotion.CONCERNED,
    (MascotEmotion.SAD,       MascotEmotion.HAPPY):     MascotEmotion.NEUTRAL,
    (MascotEmotion.SAD,       MascotEmotion.CURIOUS):   MascotEmotion.NEUTRAL,
    (MascotEmotion.CONCERNED, MascotEmotion.HAPPY):     MascotEmotion.NEUTRAL,
}


class MascotController:
    """
    Central controller handling events, transition timings, priority heaps,
    and returning snapshots for renderers.
    """
    def __init__(self, resolver: Optional[BaseEmotionResolver] = None) -> None:
        self.resolver = resolver or RuleBasedResolver()
        
        # State variables
        self.current_emotion = MascotEmotion.NEUTRAL
        self.current_activity = MascotActivity.IDLE
        self.current_presence = MascotPresence.ENGAGED

        self.emotion_start_time = 0.0
        self._event_counter = 0
        self._queue: list[tuple[int, float, int, MascotEvent]] = []
        self._is_initialized = False

    # ── Lifecycle ────────────────────────────────────────────────────────

    def initialize(self) -> None:
        self._queue.clear()
        self.current_emotion = MascotEmotion.NEUTRAL
        self.current_activity = MascotActivity.IDLE
        self.current_presence = MascotPresence.ENGAGED
        self.emotion_start_time = time.time()
        self._is_initialized = True

    def reset(self) -> None:
        self.initialize()

    def shutdown(self) -> None:
        self._queue.clear()
        self._is_initialized = False

    # ── Event queueing ───────────────────────────────────────────────────

    def handle_event(
        self,
        event_type: MascotEventType,
        payload: Optional[dict[str, Any]] = None,
        expiry_ms: float = 3000.0
    ) -> None:
        """Enqueue an event using its resolved priority."""
        if not self._is_initialized:
            self.initialize()

        # Priority mappings
        priority_map = {
            MascotEventType.LOW_CONFIDENCE:    EventPriority.HIGH,
            MascotEventType.EXPLICIT_EMOTION:  EventPriority.HIGH,
            MascotEventType.AI_SPEECH_STARTED: EventPriority.NORMAL,
            MascotEventType.SPEECH_STARTED:    EventPriority.NORMAL,
            MascotEventType.THINKING_STARTED:  EventPriority.LOW,
            MascotEventType.AI_TEXT_CHUNK:     EventPriority.LOW,
            MascotEventType.AI_SPEECH_ENDED:   EventPriority.LOW,
            MascotEventType.SPEECH_ENDED:      EventPriority.LOW,
        }
        priority = priority_map.get(event_type, EventPriority.LOW)
        now = time.time()

        event = MascotEvent(
            event_type=event_type,
            priority=priority,
            timestamp=now,
            expiry_time_ms=expiry_ms,
            payload=payload
        )

        self._event_counter += 1
        # Push into heap. heapq is min-heap: use negative priority to pop highest first.
        # FIFO for same priority is naturally handled by timestamp.
        heapq.heappush(self._queue, (-priority.value, now, self._event_counter, event))

    # ── Tick update & Snapshot generation ─────────────────────────────────

    def update(self, dt: float) -> MascotSnapshot:
        """Processes event queue, computes timings/transitions, and returns a new snapshot."""
        if not self._is_initialized:
            self.initialize()

        now = time.time()
        self._process_queue(now)

        # Look configs
        emotion_cfg = EMOTION_CONFIGS[self.current_emotion]
        activity_cfg = ACTIVITY_CONFIGS[self.current_activity]
        presence_cfg = PRESENCE_CONFIGS[self.current_presence]

        # Speaking openness
        target_open = 0.0
        if self.current_activity == MascotActivity.SPEAKING:
            # Maximum speech mouth open
            target_open = 0.55

        # Render-only Snapshot creation
        return MascotSnapshot(
            emotion=self.current_emotion,
            activity=self.current_activity,
            presence=self.current_presence,
            
            mouth_curve=emotion_cfg.mouth_curve,
            brow_raise=emotion_cfg.brow_raise,
            brow_furrow=emotion_cfg.brow_furrow,
            mouth_open=target_open,
            
            head_tilt=activity_cfg.head_tilt * presence_cfg.posture_mult,
            
            primary_accent=emotion_cfg.primary_accent,
            secondary_accent=emotion_cfg.secondary_accent,
            eye_glow=emotion_cfg.eye_glow,
            pulse_color=emotion_cfg.pulse_color,
            
            glow_intensity=emotion_cfg.glow_intensity,
            blink_rate=emotion_cfg.blink_rate,
            breathe_amp=activity_cfg.breathe_amp,
            breathe_speed_mult=presence_cfg.breathe_speed_mult,
            
            eye_x_offset=activity_cfg.base_eye_x,
            eye_y_offset=activity_cfg.base_eye_y,
            eye_wander_mult=presence_cfg.eye_wander_mult,
            
            transition_speed=emotion_cfg.transition_speed,
            timestamp=now
        )

    def _process_queue(self, now: float) -> None:
        """Filters expired events, de-duplicates them, and resolves active states."""
        # 1. Discard expired events
        valid_items = []
        for pri, ts, idx, evt in self._queue:
            if not evt.is_expired(now):
                valid_items.append((pri, ts, idx, evt))
        
        # 2. De-duplicate: Keep only latest/highest priority for each event type
        unique_evts: dict[MascotEventType, tuple[int, float, int, MascotEvent]] = {}
        for pri, ts, idx, evt in valid_items:
            existing = unique_evts.get(evt.event_type)
            if not existing or existing[0] > pri or (existing[0] == pri and existing[1] < ts):
                unique_evts[evt.event_type] = (pri, ts, idx, evt)
        
        self._queue = list(unique_evts.values())
        heapq.heapify(self._queue)

        # 3. Resolve active activity and emotion
        target_activity = MascotActivity.IDLE
        target_emotion = MascotEmotion.NEUTRAL
        
        # Check active states in the queue
        has_low_confidence = MascotEventType.LOW_CONFIDENCE in unique_evts
        has_ai_speech      = MascotEventType.AI_SPEECH_STARTED in unique_evts
        has_user_speech    = MascotEventType.SPEECH_STARTED in unique_evts
        has_thinking       = MascotEventType.THINKING_STARTED in unique_evts
        has_explicit       = MascotEventType.EXPLICIT_EMOTION in unique_evts

        # Determine Activity based on hierarchy: SPEAKING > LISTENING > THINKING > IDLE
        if has_ai_speech:
            target_activity = MascotActivity.SPEAKING
        elif has_user_speech:
            target_activity = MascotActivity.LISTENING
        elif has_thinking:
            target_activity = MascotActivity.THINKING

        # Resolve Emotion
        if has_low_confidence:
            # Microphone/quality error triggers a concerned state
            target_emotion = MascotEmotion.CONCERNED
        elif has_explicit:
            evt = unique_evts[MascotEventType.EXPLICIT_EMOTION][3]
            target_emotion = evt.payload.get("emotion", MascotEmotion.NEUTRAL)
        elif has_ai_speech or has_thinking or has_user_speech:
            # Extract text to analyze via resolver
            chunk_evt = unique_evts.get(MascotEventType.AI_TEXT_CHUNK)
            text = chunk_evt[3].payload.get("text", "") if chunk_evt else ""
            
            # Map signal
            signal = MascotSignal(text=text)
            target_emotion = self.resolver.resolve(signal)
            
            # If text sentiment says Neutral but we had a low-confidence issue earlier,
            # stay Concerned or Confused
            if target_emotion == MascotEmotion.NEUTRAL and has_low_confidence:
                target_emotion = MascotEmotion.CONCERNED

        # 4. Enforce timing constraints on Emotion transitions
        current_cfg = EMOTION_CONFIGS[self.current_emotion]
        held_duration = (now - self.emotion_start_time) * 1000.0

        if held_duration >= current_cfg.hold_duration_ms:
            # We can transition. Check the routing graph for intermediate routing path
            next_step = EMOTION_ROUTING.get((self.current_emotion, target_emotion), target_emotion)
            if next_step != self.current_emotion:
                self.current_emotion = next_step
                self.emotion_start_time = now

        # Update Activity (changes instantly for maximum responsiveness)
        self.current_activity = target_activity
