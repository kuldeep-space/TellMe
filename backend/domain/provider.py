"""
Domain Model: AI Provider Interfaces.

Defines the structure for provider-agnostic model configuration and capabilities.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

class ProviderType(Enum):
    LOCAL = "local"
    API = "api"

@dataclass
class ProviderCapability:
    """Capabilities supported by a specific provider or inference engine."""
    supports_streaming: bool = False
    supports_json_mode: bool = False
    supports_function_calling: bool = False
    supports_vision: bool = False
    max_context_length: int = 4096
    max_output_tokens: int = 1024

class FieldType(Enum):
    TEXT = "text"
    PASSWORD = "password"
    NUMBER = "number"
    SELECT = "select"
    TOGGLE = "toggle"

@dataclass
class SchemaField:
    """A dynamic configuration field required by a provider."""
    id: str
    label: str
    type: FieldType
    default: Any = None
    options: Optional[List[str]] = None
    description: str = ""

@dataclass
class ConfigurationSchema:
    """The schema defining what inputs a provider requires."""
    fields: List[SchemaField] = field(default_factory=list)

class AIProvider:
    """
    Base protocol/interface for all AI providers.
    Both Local inference engines (llama.cpp) and API providers (OpenAI, Gemini)
    implement this interface so the UI remains completely provider-agnostic.
    """
    
    @property
    def id(self) -> str:
        """Unique identifier for the provider (e.g., 'openai', 'llama_cpp')."""
        raise NotImplementedError
        
    @property
    def name(self) -> str:
        """Display name (e.g., 'OpenAI API', 'llama.cpp (Local)')."""
        raise NotImplementedError
        
    @property
    def provider_type(self) -> ProviderType:
        """Whether this is a local engine or external API."""
        raise NotImplementedError

    def get_capabilities(self) -> ProviderCapability:
        """Return the capabilities supported by this provider."""
        raise NotImplementedError
        
    def get_config_schema(self) -> ConfigurationSchema:
        """Return the dynamic configuration fields required."""
        raise NotImplementedError
