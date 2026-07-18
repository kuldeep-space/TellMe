"""
Application Lifecycle Manager.

Manages the startup and graceful shutdown sequence for TellMe.

Responsibilities:
  - Execute ordered startup hooks (database init, model pre-loading).
  - Execute ordered shutdown hooks (flush caches, close DB connections,
    unload models from memory).
  - Ensure no data corruption on unexpected termination.

Usage:
    lifecycle = ApplicationLifecycle(container)
    lifecycle.startup()
    # ... application runs ...
    lifecycle.shutdown()
"""

from backend.core.container import ServiceContainer
from backend.core.logging import get_logger

_logger = get_logger(__name__)


class ApplicationLifecycle:
    """
    Manages the ordered startup and graceful shutdown of TellMe services.

    Each phase (startup, shutdown) executes a list of named hooks in sequence.
    Hooks are registered in `bootstrap.py` and executed here.

    This class ensures that resources (database connections, loaded model
    weights, open file handles) are always released cleanly, even on
    unexpected interrupts.

    Attributes:
        _container: The application service container.
        _startup_hooks: Ordered list of (name, callable) startup actions.
        _shutdown_hooks: Ordered list of (name, callable) shutdown actions.
    """

    def __init__(self, container: ServiceContainer) -> None:
        """
        Initialize the lifecycle manager.

        Args:
            container: The fully wired application service container.
        """
        self._container = container
        self._startup_hooks: list[tuple[str, callable]] = []
        self._shutdown_hooks: list[tuple[str, callable]] = []

    def register_startup_hook(self, name: str, hook: callable) -> None:
        """
        Register a callable to be executed during application startup.

        Hooks are executed in the order they are registered.

        Args:
            name: A descriptive name for this hook (used in log output).
            hook: A zero-argument callable to execute at startup.
        """
        self._startup_hooks.append((name, hook))

    def register_shutdown_hook(self, name: str, hook: callable) -> None:
        """
        Register a callable to be executed during application shutdown.

        Shutdown hooks are executed in REVERSE registration order to ensure
        that resources are released in the correct dependency order.

        Args:
            name: A descriptive name for this hook.
            hook: A zero-argument callable to execute at shutdown.
        """
        self._shutdown_hooks.append((name, hook))

    def startup(self) -> None:
        """
        Execute all registered startup hooks in registration order.

        Any hook that raises an exception will halt the startup sequence
        and propagate the error to the caller.
        """
        _logger.info("Application startup sequence initiated.")
        for name, hook in self._startup_hooks:
            _logger.info("Running startup hook: {}", name)
            hook()
        _logger.info("All startup hooks completed successfully.")

    def shutdown(self) -> None:
        """
        Execute all registered shutdown hooks in reverse order.

        Errors in individual hooks are caught and logged to prevent one
        failing hook from blocking the cleanup of remaining resources.
        """
        _logger.info("Application shutdown sequence initiated.")
        for name, hook in reversed(self._shutdown_hooks):
            _logger.info("Running shutdown hook: {}", name)
            try:
                hook()
            except Exception as exc:  # noqa: BLE001
                _logger.error("Shutdown hook '{}' raised an error: {}", name, exc)
        _logger.info("Shutdown sequence complete.")
