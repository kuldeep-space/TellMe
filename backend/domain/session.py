"""
Domain Model: Interview Session.

Represents a single interview session instance as a pure domain entity.
Contains no database or framework imports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from backend.shared.enums.session import DifficultyLevel, InterviewType, SessionStatus


@dataclass
class InterviewSession:
    """
    Core domain entity representing one interview session lifecycle.

    An InterviewSession is the aggregate root for all session-related
    data. It tracks status transitions, timing, and links to the
    blueprint and resume used to configure the session.

    Attributes:
        session_id: Unique identifier for this session.
        user_id: ID of the user who owns this session.
        interview_type: The type of interview being conducted.
        difficulty: The configured difficulty level.
        status: The current lifecycle state of the session.
        blueprint_id: Optional ID of the blueprint used.
        resume_id: Optional ID of the resume used.
        started_at: Timestamp when the session began.
        ended_at: Timestamp when the session concluded (None if active).
        duration_minutes: Configured time limit for the session.
        title: Human-readable label for this session.
        created_at: When this record was first created.
    """

    user_id: UUID
    interview_type: InterviewType
    difficulty: DifficultyLevel
    duration_minutes: int = 45
    title: str = "Interview Session"
    blueprint_id: UUID | None = None
    resume_id: UUID | None = None
    session_id: UUID = field(default_factory=uuid4)
    status: SessionStatus = field(default=SessionStatus.PENDING)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def start(self) -> None:
        """Transition the session to ACTIVE state and record the start time."""
        if self.status != SessionStatus.PENDING:
            raise ValueError(f"Cannot start a session in '{self.status}' state.")
        self.status = SessionStatus.ACTIVE
        self.started_at = datetime.utcnow()

    def end(self) -> None:
        """Transition the session to COMPLETED state and record the end time."""
        if self.status not in (SessionStatus.ACTIVE, SessionStatus.PAUSED):
            raise ValueError(f"Cannot end a session in '{self.status}' state.")
        self.status = SessionStatus.COMPLETED
        self.ended_at = datetime.utcnow()

    def abandon(self) -> None:
        """Mark the session as ABANDONED (user-initiated early termination)."""
        self.status = SessionStatus.ABANDONED
        self.ended_at = datetime.utcnow()

    def mark_error(self) -> None:
        """Mark the session as ERROR (system-initiated termination)."""
        self.status = SessionStatus.ERROR
        self.ended_at = datetime.utcnow()

    @property
    def is_active(self) -> bool:
        """Return True if the session is currently in ACTIVE state."""
        return self.status == SessionStatus.ACTIVE

    @property
    def elapsed_seconds(self) -> float | None:
        """Return the elapsed time in seconds if the session has started."""
        if self.started_at is None:
            return None
        end = self.ended_at or datetime.utcnow()
        return (end - self.started_at).total_seconds()
