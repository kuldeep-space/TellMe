"""
Interview Validators.

Contains pure functions or classes for validating session states,
inputs, or transcript limits before taking action.
"""

from uuid import UUID

from backend.domain.session import InterviewSession
from backend.services.interview.exceptions import InvalidStateTransitionError


def ensure_can_start(session: InterviewSession) -> None:
    """
    Validate that the session is in a valid state to be started.

    Args:
        session: The session entity to validate.

    Raises:
        InvalidStateTransitionError: If the session cannot be started.
    """
    if session.is_active:
        raise InvalidStateTransitionError("Session is already active.")
