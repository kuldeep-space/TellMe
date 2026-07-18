from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum

# --- Strongly Typed Exceptions ---

class ProviderError(Exception):
    """Base class for all provider exceptions."""
    pass

class ConnectionError(ProviderError):
    pass

class AuthenticationError(ProviderError):
    pass

class RateLimitError(ProviderError):
    pass

class ModelNotFoundError(ProviderError):
    pass

class InferenceError(ProviderError):
    pass

class ConfigurationError(ProviderError):
    pass

# --- Structured Provider Data ---

@dataclass
class ProviderAction:
    """An action exposed by a provider (e.g., Refresh Models, Health Check)."""
    id: str
    display_name: str
    description: str
    icon: str = "play.svg"
    category: str = "general"
    confirmation_required: bool = False
    dangerous: bool = False
    enabled: bool = True
    visible: bool = True

@dataclass
class ModelInfo:
    """Structured metadata about an available model."""
    id: str
    display_name: str
    provider: str
    family: str = "unknown"
    parameter_size: str = "unknown"
    quantization: str = "none"
    context_length: int = 4096
    supports_vision: bool = False
    supports_reasoning: bool = False
    supports_tools: bool = False
    supports_embeddings: bool = False
    supports_audio: bool = False
    supports_image_generation: bool = False

@dataclass
class HealthStatus:
    """Rich diagnostic information returned by a health check."""
    success: bool
    status: str
    message: str
    latency: float = 0.0
    backend_version: str = "unknown"
    available_models: int = 0
    provider_version: str = "unknown"
    server_url: str = ""
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

# --- Inference Contracts ---

@dataclass
class InferenceMessage:
    role: str
    content: str
    
@dataclass
class InferenceRequest:
    """Strongly typed request sent to the AIEngine."""
    session_id: str
    system_prompt: str = ""
    user_prompt: str = ""
    messages: List[InferenceMessage] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Any] = field(default_factory=list)

@dataclass
class InferenceResponse:
    """Strongly typed response returned from non-streaming generation."""
    text: str
    finish_reason: str
    usage: Dict[str, int]
    latency: float
    model: str
    provider: str


# --- Model Library Domain ---

class ModelFormat(str, Enum):
    GGUF = "gguf"
    SAFETENSORS = "safetensors"
    ONNX = "onnx"
    GGML = "ggml"
    UNKNOWN = "unknown"

class RuntimeStatus(str, Enum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADING = "unloading"
    ERROR = "error"

@dataclass
class ModelCapabilities:
    """Static capability flags extracted or inferred during import."""
    supports_streaming: bool = True
    supports_system_prompts: bool = True
    supports_vision: bool = False
    supports_tools: bool = False
    supports_embeddings: bool = False
    context_length: int = 4096

@dataclass
class ModelDescriptor:
    """
    Immutable metadata about a registered model.
    Populated at import time and never changed thereafter.
    """
    id: str
    display_name: str
    path: str                           # Managed absolute path in TellMe model dir
    format: ModelFormat
    family: str = "unknown"             # e.g., "llama", "mistral", "phi"
    quantization: str = "unknown"       # e.g., "Q4_K_M", "Q8_0", "F16"
    parameter_size: str = "unknown"     # e.g., "7B", "13B", "70B"
    architecture: str = "unknown"       # From GGUF header: architecture key
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)
    imported_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = field(default_factory=list)
    notes: str = ""

@dataclass
class ModelState:
    """
    Volatile runtime state for a model. Changes independently of ModelDescriptor.
    Never persisted to disk.
    """
    model_id: str
    status: RuntimeStatus = RuntimeStatus.UNLOADED
    last_used: Optional[datetime] = None
    current_session_id: Optional[str] = None
    memory_usage_bytes: int = 0
    error_message: str = ""

@dataclass
class GlobalRuntimeConfig:
    """
    User-configurable inference parameters, independent of any specific model.
    Applied at generation time.
    """
    temperature: float = 0.4
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.15
    max_tokens: int = 2048
    seed: int = -1
