"""
Interview Events.

Specific payload definitions for events emitted during an interview session.
"""

from dataclasses import dataclass
from uuid import UUID

from backend.shared.events.base import BaseEvent
from backend.shared.enums.session import SessionStatus


@dataclass(frozen=True)
class SessionStateChangedEvent(BaseEvent):
    """Emitted when a session transitions (e.g. from PENDING to ACTIVE)."""

    session_id: UUID
    old_status: SessionStatus
    new_status: SessionStatus


@dataclass(frozen=True)
class TurnCompletedEvent(BaseEvent):
    """Emitted when a complete conversation turn (User or Assistant) finishes."""

    session_id: UUID
    turn_id: UUID
    role: str
