"""
Application Bootstrap.

Responsible for the one-time initialization of all application-level
services and dependencies at startup.

Responsibilities:
  1. Load environment variables and configuration.
  2. Configure logging.
  3. Ensure runtime directories exist.
  4. Wire the service container with all registered providers.
  5. Initialize the event bus.

This module does NOT start the UI. The frontend is responsible for
calling `bootstrap()` as its first action before creating any widgets.
"""

import os
import sys
from pathlib import Path

# Configure Windows DLL search path for llama_cpp local dependencies
if sys.platform == "win32":
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        local_bin_dir = project_root / "dependencies" / "llama_binaries"
        if local_bin_dir.is_dir():
            os.add_dll_directory(str(local_bin_dir))
    except Exception:
        pass

from backend.config.settings import get_settings
from backend.core.container import ServiceContainer
from backend.core.event_bus import EventBus
from backend.core.exceptions import ConfigurationError
from backend.core.logging import configure_logging, get_logger


_logger = get_logger(__name__)


def _ensure_runtime_dirs(settings) -> None:
    """
    Create all required runtime directories if they do not exist.

    Args:
        settings: The loaded AppSettings instance.

    Raises:
        ConfigurationError: If a runtime directory cannot be created.
    """
    dirs = [
        settings.runtime_cache_dir,
        settings.runtime_logs_dir,
        settings.runtime_temp_dir,
        settings.runtime_sessions_dir,
    ]
    for dir_path in dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ConfigurationError(
                f"Failed to create runtime directory '{dir_path}': {exc}"
            ) from exc


def bootstrap() -> ServiceContainer:
    """
    Initialize the TellMe application and return the wired service container.

    This function must be called exactly once at application startup before
    any service resolution occurs. It is idempotent-safe to call again in
    tests if the settings cache is cleared first.

    Returns:
        A fully wired ServiceContainer ready for dependency resolution.

    Raises:
        ConfigurationError: If required configuration is missing or invalid.
    """
    settings = get_settings()

    # Step 1: Configure logging first so all subsequent steps are logged.
    configure_logging(log_dir=settings.runtime_logs_dir, debug=settings.app_debug)
    _logger.info("Bootstrapping {} v{}", settings.app_name, settings.app_version)

    # Step 2: Ensure all runtime directories exist.
    _ensure_runtime_dirs(settings)
    _logger.info("Runtime directories verified.")

    # Step 3: Build the service container.
    container = ServiceContainer()

    # Step 4: Register the Event Bus as a singleton.
    event_bus = EventBus()
    container.register_singleton(EventBus, event_bus)

    # NOTE: Provider registrations (LLM, STT, TTS, Search, Repositories)
    # will be added here in subsequent implementation milestones.
    # Each provider will be selected based on `settings.active_llm_backend`,
    # `settings.active_stt_backend`, etc.

    _logger.info(
        "Bootstrap complete. Registered contracts: {}",
        container.registered_contracts(),
    )
    return container
