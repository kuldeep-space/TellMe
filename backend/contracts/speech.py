"""
Speech Provider Contracts.

Defines the abstract boundaries for Speech-to-Text (STT)
and Text-to-Speech (TTS) provider implementations.

Any future speech backend (Whisper, Faster-Whisper, Piper, Coqui)
must implement the corresponding contract to integrate with the
Voice Interview system.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


# ─────────────────────────────────────────────
# Data Structures
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class TranscriptionResult:
    """
    Represents the output of a Speech-to-Text transcription.

    Attributes:
        text: The transcribed text from the audio segment.
        confidence: Confidence score between 0.0 and 1.0 (if available).
        language: Detected language code (e.g., 'en').
        duration_seconds: Duration of the audio that was processed.
    """

    text: str
    confidence: float = 1.0
    language: str = "en"
    duration_seconds: float = 0.0


@dataclass(frozen=True)
class SynthesisRequest:
    """
    Represents a request to synthesize speech from text.

    Attributes:
        text: The text to convert to audio.
        voice_id: Optional identifier for the desired voice model.
        speed: Playback speed multiplier (1.0 = normal).
    """

    text: str
    voice_id: str | None = None
    speed: float = 1.0


# ─────────────────────────────────────────────
# Contracts
# ─────────────────────────────────────────────

class ISpeechToText(ABC):
    """
    Contract for all Speech-to-Text (STT) provider implementations.

    Implementations must support both single-file transcription and
    real-time streaming transcription from an audio buffer.
    """

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, sample_rate: int) -> TranscriptionResult:
        """
        Transcribe a complete audio buffer to text (blocking).

        Args:
            audio_bytes: Raw PCM audio bytes.
            sample_rate: Audio sample rate in Hz (e.g., 16000).

        Returns:
            A TranscriptionResult with the extracted text.

        Raises:
            SpeechProviderError: On transcription failure.
        """

    @abstractmethod
    def is_ready(self) -> bool:
        """Return True if the STT model is loaded and ready."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the unique identifier for this STT provider (e.g., 'whisper')."""


class ITextToSpeech(ABC):
    """
    Contract for all Text-to-Speech (TTS) provider implementations.

    Implementations must support both full synthesis and streaming
    synthesis for low-latency sentence-by-sentence audio generation.
    """

    @abstractmethod
    async def synthesize(self, request: SynthesisRequest) -> bytes:
        """
        Synthesize speech from text and return the complete audio buffer.

        Args:
            request: A SynthesisRequest containing the text and voice parameters.

        Returns:
            Raw PCM audio bytes.

        Raises:
            SpeechProviderError: On synthesis failure.
        """

    @abstractmethod
    async def stream_synthesize(self, request: SynthesisRequest) -> AsyncIterator[bytes]:
        """
        Synthesize speech and yield audio chunks as they are generated.

        Used for sentence-by-sentence streaming playback during voice
        interviews to reduce perceived latency.

        Args:
            request: A SynthesisRequest containing text and voice parameters.

        Yields:
            Raw PCM audio byte chunks.

        Raises:
            SpeechProviderError: On synthesis failure.
        """

    @abstractmethod
    def is_ready(self) -> bool:
        """Return True if the TTS engine is loaded and ready."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the unique identifier for this TTS provider (e.g., 'piper')."""
