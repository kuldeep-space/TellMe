"""
Speech Service.

High-level orchestrator for speech-to-text (STT) and text-to-speech (TTS)
operations, abstracting away the active provider.
"""

from pathlib import Path


class SpeechService:
    """
    Coordinates audio processing tasks.
    """

    def transcribe(self, audio_file: Path) -> str:
        """
        Convert audio to text using the active STT provider.

        Args:
            audio_file: Path to the recorded audio.

        Returns:
            The transcribed text.
        """
        pass
