"""
Core Service: Engine Resolver.

Responsible for dynamically selecting the best compatible inference engine
for a given ModelDescriptor based on capability scoring.

Each engine registers itself with the resolver via `EngineCapability`,
describing the formats, architectures, and priority it supports.
Adding a new engine requires NO changes to this resolver.
"""
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from backend.domain.models import ModelDescriptor, ModelFormat

logger = logging.getLogger(__name__)


@dataclass
class EngineCapability:
    """
    Self-description of an inference engine.
    Registered engines express what they can handle and their priority.
    """
    engine_id: str
    display_name: str
    supported_formats: List[ModelFormat]
    supported_architectures: List[str]   # e.g., ["llama", "mistral", "phi"] or ["*"] for any
    priority: int = 10                   # Higher = preferred when multiple engines match
    is_available: bool = True            # Can be set to False if engine is not installed


class EngineResolver:
    """
    Dynamically resolves the best compatible engine for a model.
    Uses a capability-scoring system; no hardcoded format->engine mappings.
    """
    _registry: Dict[str, EngineCapability] = {}

    @classmethod
    def register(cls, capability: EngineCapability):
        """Register an engine's capability with the resolver."""
        cls._registry[capability.engine_id] = capability
        logger.debug(f"EngineResolver: Registered engine '{capability.engine_id}' "
                     f"(formats={[f.value for f in capability.supported_formats]}, "
                     f"priority={capability.priority})")

    @classmethod
    def resolve(cls, model: ModelDescriptor) -> Optional[str]:
        """
        Evaluate all registered engines and return the engine_id of the
        best compatible one, or None if no engine can handle the model.
        """
        scored: List[tuple[int, str]] = []

        for engine_id, cap in cls._registry.items():
            if not cap.is_available:
                continue

            score = cls._score(cap, model)
            if score > 0:
                scored.append((score, engine_id))
                logger.debug(f"EngineResolver: Engine '{engine_id}' scored {score} "
                             f"for format={model.format.value}, arch={model.architecture}")

        if not scored:
            return None

        scored.sort(reverse=True, key=lambda t: t[0])
        winner = scored[0][1]
        logger.info(f"EngineResolver: Resolved '{winner}' for model '{model.id}' "
                    f"(format={model.format.value})")
        return winner

    @classmethod
    def _score(cls, cap: EngineCapability, model: ModelDescriptor) -> int:
        """
        Compute compatibility score. Returns 0 if incompatible.
        """
        # Format must match
        if model.format not in cap.supported_formats:
            return 0

        base = 100 + cap.priority

        # Bonus for exact architecture match
        arch_lower = model.architecture.lower()
        if "*" in cap.supported_architectures:
            return base
        if any(a.lower() in arch_lower or arch_lower in a.lower()
               for a in cap.supported_architectures):
            return base + 50

        # Format matched but architecture unknown/unsupported
        if model.architecture == "unknown":
            return base  # Accept with no arch bonus

        return 0  # Format matched but arch explicitly unsupported

    @classmethod
    def get_available_engines(cls) -> List[EngineCapability]:
        return [c for c in cls._registry.values() if c.is_available]

    @classmethod
    def check_availability(cls, engine_id: str) -> bool:
        cap = cls._registry.get(engine_id)
        return cap.is_available if cap else False


def _register_builtin_engines():
    """
    Register built-in engine capabilities at import time.
    Each engine declares its own formats and architectures.
    """
    # llama.cpp — handles GGUF/GGML for all common architectures
    EngineResolver.register(EngineCapability(
        engine_id="llama_cpp",
        display_name="llama.cpp",
        supported_formats=[ModelFormat.GGUF, ModelFormat.GGML],
        supported_architectures=["*"],   # llama.cpp supports all GGUF architectures
        priority=20,
        is_available=_is_llama_cpp_available(),
    ))

    # Ollama — remote runner, also handles GGUF via its own engine
    EngineResolver.register(EngineCapability(
        engine_id="ollama",
        display_name="Ollama",
        supported_formats=[ModelFormat.GGUF],
        supported_architectures=["*"],
        priority=10,
        is_available=_is_ollama_available(),
    ))


def _is_llama_cpp_available() -> bool:
    try:
        import llama_cpp  # noqa: F401
        return True
    except ImportError:
        return False


def _is_ollama_available() -> bool:
    """Check if Ollama is reachable on localhost."""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434", timeout=1)
        return True
    except Exception:
        return False


# Register engines when this module is first imported
_register_builtin_engines()
