"""
Session and Interview Enums.

Defines all status and type enumerations used across the interview
session lifecycle.
"""

from enum import Enum


class SessionStatus(str, Enum):
    """
    Represents the lifecycle state of an interview session.

    Values:
        PENDING:    Session is configured but not yet started.
        ACTIVE:     Session is currently in progress.
        PAUSED:     Session has been temporarily paused by the user.
        COMPLETED:  Session ended normally (all topics covered or time expired).
        ABANDONED:  Session was terminated early by the user.
        ERROR:      Session terminated due to an unrecoverable error.
    """

    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ERROR = "error"


class InterviewType(str, Enum):
    """
    Defines the category of interview being conducted.

    Values:
        BEHAVIORAL:     HR and soft-skills focus with STAR method enforcement.
        TECHNICAL:      Deep-dive technical knowledge in a specific stack.
        SYSTEM_DESIGN:  Open-ended architecture and scalability discussions.
        CODING:         Data structures, algorithms, and programming challenges.
        COMPANY_MOCK:   Simulates a specific company's known interview process.
        CUSTOM:         Fully user-defined topic and persona.
    """

    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    COMPANY_MOCK = "company_mock"
    CUSTOM = "custom"


class DifficultyLevel(str, Enum):
    """
    Adaptive difficulty levels for interview question generation.

    Values:
        EASY:         Entry-level; focuses on fundamentals.
        INTERMEDIATE: Mid-level; tests practical knowledge and design tradeoffs.
        HARD:         Senior/expert level; edge cases and advanced concepts.
    """

    EASY = "easy"
    INTERMEDIATE = "intermediate"
    HARD = "hard"


class TurnRole(str, Enum):
    """
    Identifies the speaker in a single conversation turn.

    Values:
        USER:       The candidate's input (text or transcribed voice).
        ASSISTANT:  The AI interviewer's response.
        SYSTEM:     Internal system instructions injected into context.
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
