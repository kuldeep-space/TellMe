"""
Domain Model: Job Description.

Represents a parsed and normalized job description used to tailor
the interview session.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class JobDescription:
    """
    Core domain entity representing a target Job Description.

    Attributes:
        job_id: Unique identifier for this job description.
        user_id: The ID of the user this job belongs to.
        source_url: Optional URL if fetched from the web.
        title: The job title (e.g., 'Senior Backend Engineer').
        company: Optional company name.
        raw_text: The original raw text.
        requirements: List of mandatory skills/qualifications.
        nice_to_haves: List of optional/bonus skills.
        is_parsed: True if the raw text has been normalized by the LLM.
        created_at: When this record was created.
    """

    user_id: UUID
    title: str = "Unknown Role"
    company: str | None = None
    source_url: str | None = None
    raw_text: str = ""
    requirements: list[str] = field(default_factory=list)
    nice_to_haves: list[str] = field(default_factory=list)
    is_parsed: bool = False
    job_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
