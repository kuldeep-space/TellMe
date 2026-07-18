"""
Base Event Payloads.

Defines the base structure for strongly typed event payloads
published over the central Event Bus.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class BaseEvent:
    """
    Base class for all events published to the Event Bus.

    Attributes:
        event_id: Unique identifier for this specific event occurrence.
        timestamp: When the event occurred (UTC).
    """

    event_id: UUID = dataclass.field(default_factory=uuid4, init=False)
    timestamp: datetime = dataclass.field(default_factory=datetime.utcnow, init=False)
