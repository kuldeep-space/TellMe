"""
Analysis Service.

Orchestrates the ingestion, parsing, and LLM normalization of
input documents (Resumes, Job Descriptions).
"""

from pathlib import Path
from uuid import UUID


class AnalysisService:
    """
    Coordinates data ingestion and normalization.
    """

    def process_resume(self, file_path: Path) -> UUID:
        """
        Parse and normalize a resume file.

        Args:
            file_path: Absolute path to the uploaded resume.

        Returns:
            The UUID of the newly created Resume domain entity.
        """
        pass
