"""
Search Provider Contract.

Defines the abstract boundary for any external information retrieval
backend (e.g., DuckDuckGo, SearXNG, custom APIs).

Search is optional; it is only activated if the user enables it in
settings and a concrete provider is registered.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SearchQuery:
    """
    Represents a search request submitted to a search provider.

    Attributes:
        query: The search query string.
        max_results: Maximum number of results to return.
        language: ISO 639-1 language code for results (e.g., 'en').
    """

    query: str
    max_results: int = 5
    language: str = "en"


@dataclass(frozen=True)
class SearchResult:
    """
    Represents a single result item from a search provider.

    Attributes:
        title: Page or result title.
        url: Source URL.
        snippet: Short text excerpt summarizing the result.
    """

    title: str
    url: str
    snippet: str


@dataclass
class SearchResponse:
    """
    Represents the full response from a search provider query.

    Attributes:
        results: List of individual search result items.
        query: The original query string that produced these results.
    """

    results: list[SearchResult] = field(default_factory=list)
    query: str = ""


class ISearchProvider(ABC):
    """
    Contract for all search/information retrieval provider implementations.

    Implementations are optional adapters that allow the AI to supplement
    its local knowledge with real-time web results.

    Providers must be registered with the ProviderRegistry at startup
    and are resolved via the ServiceContainer on demand.
    """

    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchResponse:
        """
        Execute a search and return structured results.

        Args:
            query: A SearchQuery specifying the search terms and options.

        Returns:
            A SearchResponse containing matching results.

        Raises:
            SearchProviderError: On network or API failure.
        """

    @abstractmethod
    def is_available(self) -> bool:
        """
        Return True if the search provider is reachable and operational.

        Used to gracefully degrade to local-only mode when offline.
        """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the unique identifier for this search provider (e.g., 'duckduckgo')."""
