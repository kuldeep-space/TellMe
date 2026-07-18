"""
Domain Model: Evaluation.

Represents the graded result of a completed interview session.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class EvaluationScore:
    """
    Represents a score for a specific metric.

    Attributes:
        metric: The name of the metric (e.g., 'Communication', 'Technical').
        score: Numerical score (e.g., 0-10 or 0-100).
        feedback: Textual justification for the score.
    """

    metric: str
    score: float
    feedback: str


@dataclass
class SessionEvaluation:
    """
    Core domain entity representing the final graded evaluation.

    Attributes:
        evaluation_id: Unique identifier for this evaluation.
        session_id: The interview session this evaluation grades.
        overall_score: The aggregated total score.
        scores: List of specific metric scores.
        summary: Executive summary of the candidate's performance.
        strengths: List of identified strong points.
        weaknesses: List of identified areas for improvement.
        created_at: When this evaluation was generated.
    """

    session_id: UUID
    overall_score: float = 0.0
    scores: list[EvaluationScore] = field(default_factory=list)
    summary: str = ""
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    evaluation_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
