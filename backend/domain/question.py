"""
Domain Model: Question & Transcript.

Models individual questions and conversation turns within a session.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from backend.shared.enums.session import TurnRole


@dataclass
class ConversationTurn:
    """
    Represents a single turn in the interview transcript.

    Attributes:
        turn_id: Unique identifier for this turn.
        session_id: The interview session this turn belongs to.
        role: The speaker role (User, Assistant, System).
        content: The text content of the turn.
        timestamp: When this turn was added to the transcript.
    """

    session_id: UUID
    role: TurnRole
    content: str
    turn_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
