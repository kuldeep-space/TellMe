"""
Interview Service.

Core orchestration service for managing active interview sessions.
"""

from uuid import UUID

from backend.core.event_bus import EventBus
from backend.contracts.repository import IRepository
from backend.domain.session import InterviewSession


class InterviewService:
    """
    Coordinates the lifecycle and workflow of an interview session.
    """

    def __init__(
        self,
        session_repo: IRepository[InterviewSession],
        event_bus: EventBus,
    ) -> None:
        """Initialize the service."""
        self._session_repo = session_repo
        self._event_bus = event_bus

    def start_session(self, session_id: UUID) -> None:
        """
        Start the given session and emit the appropriate event.

        Args:
            session_id: The UUID of the session to start.
        """
        pass

    def process_user_turn(self, session_id: UUID, user_text: str) -> None:
        """
        Process a user input and trigger AI generation.

        Args:
            session_id: The active session UUID.
            user_text: The user's input (transcribed or typed).
        """
        pass
