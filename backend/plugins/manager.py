"""
Plugin Manager.

Coordinates the lifecycle of all plugins, invoking loader discovery
and handling registration into the core service container.
"""

from backend.plugins.loader import PluginLoader
from backend.plugins.registry import PluginRegistry


class PluginManager:
    """
    Central orchestrator for the plugin subsystem.
    """

    def __init__(self, loader: PluginLoader, registry: PluginRegistry) -> None:
        """Initialize the manager."""
        self._loader = loader
        self._registry = registry

    def initialize_plugins(self) -> None:
        """Discover, validate, and register all enabled plugins."""
        pass

    def shutdown_plugins(self) -> None:
        """Gracefully shut down all active plugins."""
        pass
