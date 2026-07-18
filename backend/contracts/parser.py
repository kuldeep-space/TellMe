"""
Parser Contracts.

Defines abstract boundaries for all content parsing implementations.
Parsers are responsible for extracting clean, structured text from
raw binary or web content (PDF, HTML, Markdown, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class SourceType(str, Enum):
    """Enumeration of supported raw input source types."""

    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"
    GITHUB = "github"


@dataclass
class ParsedContent:
    """
    Represents the output of a successful parse operation.

    Attributes:
        raw_text: The clean, extracted plain text from the source.
        source_type: The type of the original source material.
        metadata: Optional key-value metadata extracted alongside the text.
        word_count: Approximate word count of the extracted text.
    """

    raw_text: str
    source_type: SourceType
    metadata: dict = field(default_factory=dict)

    @property
    def word_count(self) -> int:
        """Return approximate word count of the extracted text."""
        return len(self.raw_text.split())


class IParser(ABC):
    """
    Base contract for all content parser implementations.

    Parsers receive raw bytes or text and return a normalized
    ParsedContent object ready for LLM normalization.
    """

    @abstractmethod
    def parse(self, raw_input: bytes | str) -> ParsedContent:
        """
        Parse raw content and return structured plain text.

        Args:
            raw_input: Raw bytes (e.g., PDF binary) or string (e.g., HTML).

        Returns:
            A ParsedContent object with clean extracted text.

        Raises:
            ParserError: If the content cannot be parsed.
        """

    @abstractmethod
    def supports(self, source_type: SourceType) -> bool:
        """
        Return True if this parser supports the given source type.

        Used by the parser registry to select the correct parser.

        Args:
            source_type: The type of content to be parsed.

        Returns:
            True if this parser handles the given source type.
        """

    @property
    @abstractmethod
    def parser_name(self) -> str:
        """Return the unique identifier for this parser (e.g., 'pdf_pdfplumber')."""


class IResumeParser(IParser):
    """
    Specialized parser contract for resume documents.

    Extends IParser with resume-specific extraction capabilities
    such as extracting contact information, skills, and work history.
    """

    @abstractmethod
    def extract_sections(self, content: ParsedContent) -> dict[str, str]:
        """
        Extract structured sections from a parsed resume.

        Returns a dictionary with keys such as 'skills', 'experience',
        'education', and 'projects'.

        Args:
            content: A previously parsed ParsedContent from the resume file.

        Returns:
            A dictionary mapping section names to extracted text blocks.
        """
