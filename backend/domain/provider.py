"""
Domain Model: AI Provider Interfaces.

Defines the structure for provider-agnostic model configuration and capabilities.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Type, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from backend.domain.models import ProviderAction, InferenceRequest

class ProviderCategory(Enum):
    OPENAI_COMPATIBLE = "openai_compatible"
    NATIVE = "native"
    LOCAL = "local"

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
    supports_audio_in: bool = False
    supports_audio_out: bool = False
    supports_image_generation: bool = False
    supports_embeddings: bool = False
    supports_reasoning: bool = False
    supports_tool_calling: bool = False
    supports_system_prompts: bool = True
    supports_batch_requests: bool = False
    supports_file_uploads: bool = False
    max_context_length: int = 4096
    max_output_tokens: int = 1024

class FieldType(Enum):
    TEXT = "text"
    PASSWORD = "password"
    NUMBER = "number"
    SELECT = "select"
    FILE_PATH = "file_path"
    DIR_PATH = "dir_path"
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

@dataclass
class RuntimeParameterSchema:
    """Defines which runtime sliders/options are supported by the provider."""
    supports_temperature: bool = True
    supports_top_p: bool = True
    supports_top_k: bool = False
    supports_min_p: bool = False
    supports_typical_p: bool = False
    supports_repeat_penalty: bool = False
    supports_frequency_penalty: bool = False
    supports_presence_penalty: bool = False
    supports_seed: bool = False
    supports_stop_sequences: bool = True
    supports_max_tokens: bool = True
    supports_context_length: bool = True
    supports_reasoning_effort: bool = False
    supports_gpu_layers: bool = False

@dataclass
class ProviderMetadata:
    """Metadata about the provider for UI rendering."""
    id: str
    display_name: str
    category: ProviderCategory
    description: str = ""
    website: str = ""
    icon: str = "default_provider.svg"

@dataclass
class ProviderConfiguration:
    """Saved configuration instance for a provider."""
    provider_id: str
    backend_type: ProviderType
    display_name: str
    configuration: Dict[str, Any] = field(default_factory=dict)
    runtime_parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class AIProvider:
    """
    Base protocol/interface for all AI providers.
    Both Local inference engines and API providers implement this interface.
    """
    
    _registry: Dict[str, Type['AIProvider']] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # We will register them by their ID after instantiating briefly, 
        # but since we want to avoid instantiating all of them if they are heavy,
        # we can mandate that they provide a class attribute `provider_id`.
        # Alternatively, we just collect them all and register them dynamically.
        cls._registry[cls.__name__] = cls
    
    @classmethod
    def get_metadata(cls) -> ProviderMetadata:
        raise NotImplementedError
        
    def get_capabilities(self) -> ProviderCapability:
        raise NotImplementedError
        
    def get_config_schema(self) -> ConfigurationSchema:
        raise NotImplementedError
        
    def get_runtime_schema(self) -> RuntimeParameterSchema:
        return RuntimeParameterSchema() # Defaults to standard parameters
        
    def get_supported_actions(self) -> List['ProviderAction']:
        return []
        
    def execute_action(self, action_id: str, config: 'ProviderConfiguration') -> Any:
        raise NotImplementedError(f"Action {action_id} not implemented.")
        
    def stream_generate(self, request: 'InferenceRequest') -> Any:
        raise NotImplementedError
