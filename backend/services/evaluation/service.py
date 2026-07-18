"""
Evaluation Service.

Orchestrates the post-interview evaluation process, scoring transcripts
against standardized rubrics.
"""

from uuid import UUID


class EvaluationService:
    """
    Coordinates the grading of an interview transcript.
    """

    def evaluate_session(self, session_id: UUID) -> None:
        """
        Trigger an evaluation for the specified session.

        Args:
            session_id: The UUID of the session to grade.
        """
        pass
