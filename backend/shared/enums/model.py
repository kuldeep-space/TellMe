"""
Model Management Enums.

Defines enumerations related to local AI model registration,
inference backends, and runtime status.
"""

from enum import Enum


class BackendType(str, Enum):
    """
    Supported inference backend identifiers.

    These values are stored in the model registry and determine
    which concrete provider adapter is used to load and run the model.

    Values:
        LLAMACPP:   llama.cpp via llama-cpp-python bindings.
        OLLAMA:     Ollama REST API server (local or remote).
        LM_STUDIO:  LM Studio OpenAI-compatible REST endpoint.
        VLLM:       vLLM OpenAI-compatible REST endpoint.
        CUSTOM:     User-defined custom backend (via plugin).
    """

    LLAMACPP = "llamacpp"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    VLLM = "vllm"
    CUSTOM = "custom"


class ModelStatus(str, Enum):
    """
    Lifecycle status of a registered model.

    Values:
        REGISTERED: Model path is saved; not yet loaded into memory.
        LOADING:    Model is currently being loaded into the inference backend.
        READY:      Model is loaded and ready to serve inference requests.
        UNLOADING:  Model is being removed from memory.
        ERROR:      Model failed to load or validate.
    """

    REGISTERED = "registered"
    LOADING = "loading"
    READY = "ready"
    UNLOADING = "unloading"
    ERROR = "error"


class ModelArchitecture(str, Enum):
    """
    Detected neural network architecture families.

    These are populated automatically from the GGUF file header
    by the metadata extractor and stored alongside the registration.

    Note: New architectures should be added here as GGUF support expands.
    """

    LLAMA = "llama"
    QWEN = "qwen"
    MISTRAL = "mistral"
    GEMMA = "gemma"
    PHI = "phi"
    FALCON = "falcon"
    UNKNOWN = "unknown"
