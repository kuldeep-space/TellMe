"""
TellMe Global Exception Hierarchy.

All custom exceptions in TellMe inherit from TellMeError.
This allows callers to catch either the root exception or specific
sub-exceptions with precise granularity.

Exception Tree:
    TellMeError
    ├── ConfigurationError
    ├── DependencyError
    ├── StorageError
    │   └── MigrationError
    ├── ProviderError
    │   ├── LLMProviderError
    │   ├── SpeechProviderError
    │   └── SearchProviderError
    ├── ModelManagementError
    │   ├── ModelNotFoundError
    │   ├── ModelValidationError
    │   └── ModelLoadError
    ├── PluginError
    │   ├── PluginLoadError
    │   └── PluginRegistrationError
    ├── IngestionError
    │   └── ParserError
    └── ServiceError
        ├── InterviewServiceError
        ├── EvaluationServiceError
        └── AnalysisServiceError
"""


class TellMeError(Exception):
    """
    Root exception for all TellMe application errors.

    All custom exceptions must inherit from this class to allow
    callers to catch the full exception hierarchy with a single clause.
    """

    def __init__(self, message: str, context: dict | None = None) -> None:
        """
        Initialize a TellMeError.

        Args:
            message: Human-readable description of the error.
            context: Optional dictionary with additional diagnostic data.
        """
        super().__init__(message)
        self.message = message
        self.context: dict = context or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, context={self.context!r})"


# ─────────────────────────────────────────────
# Core Errors
# ─────────────────────────────────────────────

class ConfigurationError(TellMeError):
    """Raised when a required configuration key is missing or invalid."""


class DependencyError(TellMeError):
    """Raised when the service container cannot resolve a required dependency."""


# ─────────────────────────────────────────────
# Storage Errors
# ─────────────────────────────────────────────

class StorageError(TellMeError):
    """Raised on database or file system access failures."""


class MigrationError(StorageError):
    """Raised when a database migration fails to apply."""


# ─────────────────────────────────────────────
# Provider Errors
# ─────────────────────────────────────────────

class ProviderError(TellMeError):
    """Base class for all provider-level failures."""


class LLMProviderError(ProviderError):
    """Raised when the active LLM provider encounters an error."""


class SpeechProviderError(ProviderError):
    """Raised when the active STT or TTS provider encounters an error."""


class SearchProviderError(ProviderError):
    """Raised when the active search provider encounters an error."""


# ─────────────────────────────────────────────
# Model Management Errors
# ─────────────────────────────────────────────

class ModelManagementError(TellMeError):
    """Base class for local AI model management failures."""


class ModelNotFoundError(ModelManagementError):
    """Raised when a registered model ID cannot be resolved to a file."""


class ModelValidationError(ModelManagementError):
    """Raised when a GGUF file fails format or compatibility validation."""


class ModelLoadError(ModelManagementError):
    """Raised when a validated model cannot be loaded into the inference backend."""


# ─────────────────────────────────────────────
# Plugin Errors
# ─────────────────────────────────────────────

class PluginError(TellMeError):
    """Base class for plugin system failures."""


class PluginLoadError(PluginError):
    """Raised when a plugin module cannot be dynamically imported."""


class PluginRegistrationError(PluginError):
    """Raised when a plugin fails contract validation during registration."""


# ─────────────────────────────────────────────
# Ingestion Errors
# ─────────────────────────────────────────────

class IngestionError(TellMeError):
    """Raised when an input source (PDF, URL, text) cannot be fetched or parsed."""


class ParserError(IngestionError):
    """Raised when a content parser fails to extract usable text."""


# ─────────────────────────────────────────────
# Service Errors
# ─────────────────────────────────────────────

class ServiceError(TellMeError):
    """Base class for application service-level failures."""


class InterviewServiceError(ServiceError):
    """Raised when the interview service encounters an unrecoverable state."""


class EvaluationServiceError(ServiceError):
    """Raised when the evaluation service fails to grade a transcript."""


class AnalysisServiceError(ServiceError):
    """Raised when the analysis service fails to extract data from an input."""
