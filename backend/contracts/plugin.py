"""
Plugin Contract.

Defines the abstract boundary that all third-party plugins must satisfy
to integrate with the TellMe plugin system.

A plugin is any externally developed Python module that extends TellMe's
capabilities by implementing one of the core provider contracts (LLM,
Speech, Search, Parser) and registering itself via the plugin manifest.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PluginManifest:
    """
    Metadata descriptor for a discovered plugin.

    This structure is returned by every plugin's `get_manifest()` method
    and is used by the PluginManager to validate, register, and display
    information about the plugin.

    Attributes:
        name: Human-readable plugin name.
        plugin_id: Unique machine-readable identifier (e.g., 'ollama_llm').
        version: Semantic version string (e.g., '1.0.0').
        description: Short description of what the plugin provides.
        author: Plugin author name or organization.
        contract: The contract class name this plugin implements (e.g., 'ILLMProvider').
    """

    name: str
    plugin_id: str
    version: str
    description: str
    author: str
    contract: str


class IPlugin(ABC):
    """
    Base contract that all TellMe plugins must implement.

    Plugins are discovered at runtime from the configured plugins directory.
    Each plugin must declare its manifest and provide an initialized
    instance of the provider it implements.
    """

    @abstractmethod
    def get_manifest(self) -> PluginManifest:
        """
        Return the plugin's metadata manifest.

        This is called immediately after discovery to validate the plugin
        before any initialization takes place.

        Returns:
            A fully populated PluginManifest descriptor.
        """

    @abstractmethod
    def initialize(self) -> None:
        """
        Perform any one-time setup required by the plugin.

        Called once after the plugin has been validated and registered.
        May raise PluginLoadError if initialization fails.

        Raises:
            PluginLoadError: If the plugin cannot initialize successfully.
        """

    @abstractmethod
    def get_provider(self) -> object:
        """
        Return the concrete provider instance this plugin registers.

        The returned object must implement one of the core contracts
        (ILLMProvider, ISpeechToText, ITextToSpeech, ISearchProvider, IParser).

        Returns:
            The initialized provider instance.
        """

    @abstractmethod
    def shutdown(self) -> None:
        """
        Perform any cleanup required when the plugin is unloaded.

        Called during application shutdown or if the plugin is explicitly
        deactivated by the user.
        """
