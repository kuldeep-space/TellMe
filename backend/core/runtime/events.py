import dataclasses
from typing import Any, Dict, Optional
from datetime import datetime, timezone

@dataclasses.dataclass(frozen=True)
class RuntimeEvent:
    timestamp: datetime = dataclasses.field(init=False, default_factory=lambda: datetime.now(timezone.utc))

@dataclasses.dataclass(frozen=True)
class ModelLoaded(RuntimeEvent):
    model_id: str
    engine_id: str
    context_length: int

@dataclasses.dataclass(frozen=True)
class ModelUnloaded(RuntimeEvent):
    model_id: str

@dataclasses.dataclass(frozen=True)
class ContextReduced(RuntimeEvent):
    model_id: str
    requested_context: int
    actual_context: int
    reason: str

@dataclasses.dataclass(frozen=True)
class GenerationStarted(RuntimeEvent):
    model_id: str
    prompt_length: int

@dataclasses.dataclass(frozen=True)
class GenerationFinished(RuntimeEvent):
    model_id: str
    tokens_generated: int
    total_time_sec: float

@dataclasses.dataclass(frozen=True)
class GenerationCancelled(RuntimeEvent):
    model_id: str

@dataclasses.dataclass(frozen=True)
class DiagnosticsUpdated(RuntimeEvent):
    model_id: str
    diagnostics: Any  # RuntimeDiagnostics

@dataclasses.dataclass(frozen=True)
class RuntimeWarning(RuntimeEvent):
    message: str
    source: str

@dataclasses.dataclass(frozen=True)
class RuntimeErrorEvent(RuntimeEvent):
    error: str
    source: str
    details: Optional[Dict[str, Any]] = None

class EventBus:
    """Central event bus for the runtime architecture."""
    _subscribers = []

    @classmethod
    def subscribe(cls, callback):
        cls._subscribers.append(callback)

    @classmethod
    def unsubscribe(cls, callback):
        if callback in cls._subscribers:
            cls._subscribers.remove(callback)

    @classmethod
    def publish(cls, event: RuntimeEvent):
        for sub in cls._subscribers:
            try:
                sub(event)
            except Exception as e:
                # Log but do not interrupt event publishing
                print(f"EventBus: Subscriber error: {e}")
