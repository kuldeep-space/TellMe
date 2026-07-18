import dataclasses
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime

class SessionState(Enum):
    CREATED = "Created"
    INITIALIZING = "Initializing"
    LOADING = "Loading"
    READY = "Ready"
    GENERATING = "Generating"
    CANCELLING = "Cancelling"
    UNLOADING = "Unloading"
    CLOSED = "Closed"
    FAILED = "Failed"

@dataclasses.dataclass(frozen=True)
class EngineCapabilities:
    supports_gpu_layers: bool
    supports_flash_attention: bool
    supports_embeddings: bool
    supports_streaming: bool
    supports_mmap: bool
    supports_mlock: bool
    supports_batching: bool
    supports_vision: bool
    supports_tool_calling: bool

@dataclasses.dataclass(frozen=True)
class MemoryPolicy:
    safety_margin_percent: float = 0.10
    minimum_free_memory_mb: int = 500
    emergency_margin_mb: int = 100
    allow_user_override: bool = False
    allow_unsafe_loading: bool = False
    maximum_memory_utilization: float = 0.95

@dataclasses.dataclass(frozen=True)
class RuntimePlan:
    # General
    engine_id: str
    backend_version: str

    # Model
    model_id: str
    model_path: str
    architecture: str

    # Execution
    context_length: int
    batch_size: int
    ubatch_size: int
    thread_count: int
    thread_batch_count: int
    gpu_layers: int

    # Memory
    estimated_memory_mb: float
    available_memory_mb: float
    safety_margin_mb: float

    # Features
    use_mmap: bool
    use_mlock: bool
    use_flash_attention: bool
    
    # Warnings
    context_reduced: bool
    policy_overrides: List[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class RuntimeDiagnostics:
    engine: str
    backend_version: str
    runtime_version: str
    
    model_name: str
    architecture: str
    quantization: str
    model_size_mb: float

    requested_context: int
    actual_context: int
    batch_size: int
    thread_configuration: str
    gpu_layers: int

    estimated_memory_mb: float
    actual_memory_mb: float
    available_ram_before_mb: float
    available_ram_after_mb: float
    kv_cache_estimate_mb: float
    compute_buffer_estimate_mb: float

    load_time_sec: float
    initialization_time_sec: float

    context_reduced: bool
    unsafe_configuration: bool
    policy_overrides: List[str]

@dataclasses.dataclass(frozen=True)
class InferenceRequest:
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.95
    stop_sequences: List[str] = dataclasses.field(default_factory=list)
    stream: bool = True

@dataclasses.dataclass(frozen=True)
class InferenceResponse:
    text: str
    finish_reason: Optional[str]
    usage: Dict[str, int]
