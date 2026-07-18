"""
TellMe Contracts Package.

Exports all boundary contracts (abstract interfaces) for the TellMe system.
Every concrete provider, repository, and plugin implementation must satisfy
one of these contracts.
"""

from backend.contracts.llm import ILLMProvider, LLMRequest, LLMResponse
from backend.contracts.speech import (
    ISpeechToText,
    ITextToSpeech,
    TranscriptionResult,
    SynthesisRequest,
)
from backend.contracts.search import ISearchProvider, SearchQuery, SearchResult, SearchResponse
from backend.contracts.parser import IParser, IResumeParser, ParsedContent, SourceType
from backend.contracts.repository import IRepository
from backend.contracts.plugin import IPlugin, PluginManifest

__all__ = [
    "ILLMProvider", "LLMRequest", "LLMResponse",
    "ISpeechToText", "ITextToSpeech", "TranscriptionResult", "SynthesisRequest",
    "ISearchProvider", "SearchQuery", "SearchResult", "SearchResponse",
    "IParser", "IResumeParser", "ParsedContent", "SourceType",
    "IRepository",
    "IPlugin", "PluginManifest",
]
