from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, Optional
from backend.core.runtime.models import (
    RuntimePlan, InferenceRequest, InferenceResponse, EngineCapabilities,
    SessionState, RuntimeDiagnostics
)
from backend.core.runtime.memory import BaseMemoryEstimator

class RuntimeSession(ABC):
    """
    Represents an active loaded model session.
    Owns the loaded model instance, generation state, and lifetime.
    """
    @property
    @abstractmethod
    def plan(self) -> RuntimePlan:
        pass

    @property
    @abstractmethod
    def state(self) -> SessionState:
        pass

    @property
    @abstractmethod
    def diagnostics(self) -> Optional[RuntimeDiagnostics]:
        pass

    @abstractmethod
    def generate(self, request: InferenceRequest) -> Iterator[InferenceResponse]:
        """Generate text from the model."""
        pass

    @abstractmethod
    def cancel(self):
        """Cancel the current generation."""
        pass

    @abstractmethod
    def shutdown(self):
        """Unload the model and release all native resources cleanly."""
        pass


class RuntimeEngine(ABC):
    """
    Represents a specific inference backend implementation (e.g. llama.cpp, vLLM).
    Responsible for initializing the backend and creating RuntimeSessions.
    """
    @abstractmethod
    def initialize(self):
        """Initialize the backend engine globally if necessary."""
        pass

    @abstractmethod
    def get_capabilities(self) -> EngineCapabilities:
        """Return the capabilities supported by this engine."""
        pass

    @abstractmethod
    def create_memory_estimator(self) -> BaseMemoryEstimator:
        """Return an engine-specific memory estimator."""
        pass

    @abstractmethod
    def load_model(self, plan: RuntimePlan) -> RuntimeSession:
        """Load a model according to the RuntimePlan and return an isolated session."""
        pass

    @abstractmethod
    def shutdown(self):
        """Shutdown the engine globally."""
        pass
