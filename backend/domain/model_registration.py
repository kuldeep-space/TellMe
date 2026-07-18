"""
Domain Model: Model Registration.

Represents a user-registered local AI model entry.
This is completely model-agnostic; all architecture information
is detected from the binary file and stored here.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from backend.shared.enums.model import BackendType, ModelArchitecture, ModelStatus


@dataclass
class ModelRuntimeConfig:
    """
    Runtime configuration parameters for a registered model.

    These values control how the model is loaded into memory
    and how inference is executed. They are stored per-registration
    so users can tune each model independently.

    Attributes:
        gpu_layers: Number of transformer layers to offload to GPU (0 = CPU only).
        context_length: Active context window size in tokens.
        max_tokens: Default maximum tokens to generate per response.
        temperature: Default sampling temperature.
        top_p: Default nucleus sampling probability.
        repeat_penalty: Default repetition penalty multiplier.
        threads: Number of CPU threads to use (0 = auto-detect).
    """

    gpu_layers: int = 0
    context_length: int = 4096
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9
    repeat_penalty: float = 1.1
    threads: int = 0


@dataclass
class ModelRegistration:
    """
    Domain entity representing a user-registered local AI model.

    This entity is model-agnostic. Architecture and metadata are
    populated automatically by the metadata extractor when the user
    selects a GGUF file, not hardcoded anywhere.

    Attributes:
        model_id: Unique identifier for this registration.
        display_name: User-assigned friendly name for this model.
        model_path: Absolute path to the GGUF file on the filesystem.
        backend: The inference backend used to run this model.
        architecture: Detected architecture family from file headers.
        status: Current lifecycle status of this registration.
        metadata: Raw key-value metadata extracted from the GGUF headers.
        runtime_config: Tunable inference parameters for this model.
        registered_at: When this model was first registered.
        last_used_at: When this model was last selected as active.
    """

    display_name: str
    model_path: Path
    backend: BackendType
    model_id: UUID = field(default_factory=uuid4)
    architecture: ModelArchitecture = ModelArchitecture.UNKNOWN
    status: ModelStatus = ModelStatus.REGISTERED
    metadata: dict = field(default_factory=dict)
    runtime_config: ModelRuntimeConfig = field(default_factory=ModelRuntimeConfig)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_used_at: datetime | None = None

    @property
    def filename(self) -> str:
        """Return the model filename without directory path."""
        return self.model_path.name

    @property
    def is_ready(self) -> bool:
        """Return True if the model is in READY state."""
        return self.status == ModelStatus.READY

    def mark_ready(self) -> None:
        """Transition model status to READY."""
        self.status = ModelStatus.READY

    def mark_error(self) -> None:
        """Transition model status to ERROR."""
        self.status = ModelStatus.ERROR

    def touch(self) -> None:
        """Update the last_used_at timestamp to now."""
        self.last_used_at = datetime.utcnow()
