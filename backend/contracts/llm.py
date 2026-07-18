"""
LLM Provider Contract.

Defines the abstract boundary between the application core and any
Large Language Model inference backend (llama.cpp, Ollama, LM Studio, vLLM).

Any new LLM backend must implement `ILLMProvider` to be compatible
with the interview engine, evaluation engine, and analysis services.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMRequest:
    """
    Encapsulates a single inference request to the LLM.

    Attributes:
        prompt: The fully formatted prompt string to send.
        max_tokens: Maximum number of tokens to generate.
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).
        top_p: Nucleus sampling probability threshold.
        repeat_penalty: Penalty multiplier to reduce repetitive output.
        stop_sequences: List of strings that signal the model to stop generating.
    """

    prompt: str
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9
    repeat_penalty: float = 1.1
    stop_sequences: tuple[str, ...] = ()


@dataclass(frozen=True)
class LLMResponse:
    """
    Encapsulates the complete response from an LLM inference call.

    Attributes:
        text: The full generated text output.
        tokens_generated: Number of tokens produced in this response.
        tokens_prompt: Number of tokens consumed from the prompt.
        finish_reason: Why generation stopped (e.g., "stop", "length").
    """

    text: str
    tokens_generated: int
    tokens_prompt: int
    finish_reason: str


class ILLMProvider(ABC):
    """
    Contract for all Large Language Model inference providers.

    Implementations must support both batch generation and token streaming,
    as well as token counting for context window management.

    All providers are registered with the ProviderRegistry and resolved
    at runtime via the ServiceContainer.
    """

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a complete response for the given request (blocking).

        Args:
            request: The fully specified inference request.

        Returns:
            A complete LLMResponse including generated text and metadata.

        Raises:
            LLMProviderError: On any inference failure.
        """

    @abstractmethod
    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """
        Stream response tokens one at a time (non-blocking generator).

        This is the preferred method for real-time voice conversations
        where the TTS pipeline needs tokens as they are generated.

        Args:
            request: The fully specified inference request.

        Yields:
            Individual text tokens as they are generated.

        Raises:
            LLMProviderError: On any inference failure.
        """

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in the given text string.

        Used by the ContextBuilder to track and manage context window usage.

        Args:
            text: Raw text to tokenize and count.

        Returns:
            The integer token count.
        """

    @abstractmethod
    def is_ready(self) -> bool:
        """
        Return True if the provider is initialized and ready to serve requests.

        Used by the lifecycle manager to check readiness before starting a session.
        """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the unique identifier string for this provider (e.g., 'llamacpp')."""

    @property
    @abstractmethod
    def context_window(self) -> int:
        """Return the maximum supported context window size in tokens."""
