"""
Plugin Registry.

Tracks all successfully loaded third-party plugins and maps them
to the internal contracts they fulfill.
"""

from backend.contracts.plugin import IPlugin, PluginManifest


class PluginRegistry:
    """
    Maintains the catalog of active third-party plugins.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._plugins: dict[str, IPlugin] = {}

    def register(self, plugin: IPlugin) -> None:
        """Register a validated plugin."""
        pass

    def get_manifests(self) -> list[PluginManifest]:
        """Return metadata for all registered plugins."""
        return []
