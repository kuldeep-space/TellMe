"""
Domain Model: Resume.

Represents a candidate's resume, either uploaded as a raw file
or parsed into structured sections.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Resume:
    """
    Core domain entity representing a Candidate's resume.

    Attributes:
        resume_id: Unique identifier for this resume record.
        user_id: The ID of the user this resume belongs to.
        filename: Original filename of the uploaded document.
        raw_text: Extracted plain text from the document.
        structured_data: JSON-normalized structured sections (e.g., skills, history).
        is_parsed: True if the resume has been successfully normalized by the LLM.
        created_at: When the resume was uploaded.
    """

    user_id: UUID
    filename: str
    raw_text: str = ""
    structured_data: dict = field(default_factory=dict)
    is_parsed: bool = False
    resume_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
