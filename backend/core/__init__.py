"""
TellMe Core Package.

Exports the primary application-level infrastructure components:
  - ServiceContainer: Dependency Injection container.
  - EventBus: Publish/Subscribe event dispatcher.
  - configure_logging: Logging setup function.
  - TellMeError and full exception hierarchy.
"""

from backend.core.container import ServiceContainer
from backend.core.event_bus import EventBus
from backend.core.exceptions import (
    TellMeError,
    ConfigurationError,
    DependencyError,
    StorageError,
    MigrationError,
    ProviderError,
    LLMProviderError,
    SpeechProviderError,
    SearchProviderError,
    ModelManagementError,
    ModelNotFoundError,
    ModelValidationError,
    ModelLoadError,
    PluginError,
    PluginLoadError,
    PluginRegistrationError,
    IngestionError,
    ParserError,
    ServiceError,
    InterviewServiceError,
    EvaluationServiceError,
    AnalysisServiceError,
)
from backend.core.logging import configure_logging, get_logger, get_ai_logger

__all__ = [
    "ServiceContainer",
    "EventBus",
    "configure_logging",
    "get_logger",
    "get_ai_logger",
    "TellMeError",
    "ConfigurationError",
    "DependencyError",
    "StorageError",
    "MigrationError",
    "ProviderError",
    "LLMProviderError",
    "SpeechProviderError",
    "SearchProviderError",
    "ModelManagementError",
    "ModelNotFoundError",
    "ModelValidationError",
    "ModelLoadError",
    "PluginError",
    "PluginLoadError",
    "PluginRegistrationError",
    "IngestionError",
    "ParserError",
    "ServiceError",
    "InterviewServiceError",
    "EvaluationServiceError",
    "AnalysisServiceError",
]
