"""
Interview Exceptions.

Defines exceptions isolated strictly to the Interview feature.
"""

from backend.core.exceptions import InterviewServiceError


class SessionNotFoundError(InterviewServiceError):
    """Raised when an operation is attempted on an unknown session."""


class InvalidStateTransitionError(InterviewServiceError):
    """Raised when an illegal lifecycle transition is attempted (e.g., end() on a PENDING session)."""
