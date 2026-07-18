"""
Core Service: Model Registry.

Single source of truth for all registered models in TellMe.
Manages model persistence (models.json) via ModelDatabase.
Only responsible for storage and lookup — not import orchestration.
"""
import os
import json
import logging
import dataclasses
from typing import List, Optional, Dict
from datetime import datetime, timezone
from backend.domain.models import (
    ModelDescriptor, ModelCapabilities, ModelFormat
)

logger = logging.getLogger(__name__)

_REGISTRY_DIR  = os.path.join(os.path.dirname(__file__), "..", "..", "runtime")
_REGISTRY_PATH = os.path.join(_REGISTRY_DIR, "models.json")
_MODELS_DIR    = os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "models")


class ModelDatabase:
    """
    Handles read/write of the models.json registry file.
    All paths stored are absolute to avoid broken references.
    """

    def __init__(self, registry_path: str = _REGISTRY_PATH):
        self._path = os.path.abspath(registry_path)
        os.makedirs(os.path.dirname(self._path), exist_ok=True)

    def load_all(self) -> List[ModelDescriptor]:
        if not os.path.exists(self._path):
            return []
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [self._deserialize(entry) for entry in data]
        except Exception as e:
            logger.error(f"ModelDatabase: Failed to read registry: {e}")
            return []

    def save_all(self, models: List[ModelDescriptor]):
        try:
            data = [self._serialize(m) for m in models]
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"ModelDatabase: Failed to write registry: {e}")
            raise RuntimeError(f"Registry persistence failed: {e}") from e

    def _serialize(self, m: ModelDescriptor) -> dict:
        from typing import Dict, Any
        d: Dict[str, Any] = dataclasses.asdict(m)
        d["format"] = m.format.value
        d["imported_at"] = m.imported_at.isoformat()
        return d

    def _deserialize(self, d: dict) -> ModelDescriptor:
        caps_data = d.pop("capabilities", {})
        caps = ModelCapabilities(**caps_data)
        d["format"] = ModelFormat(d.get("format", "unknown"))
        imported_raw = d.pop("imported_at", None)
        imported_at = datetime.fromisoformat(imported_raw) if imported_raw else datetime.now(timezone.utc)
        return ModelDescriptor(**d, capabilities=caps, imported_at=imported_at)


class ModelRegistry:
    """
    Registry for all models available in TellMe.
    Thread-safe for reads; assumes single-writer (main thread) for writes.
    """
    _instance: Optional["ModelRegistry"] = None

    def __init__(self):
        self._db = ModelDatabase()
        self._models: Dict[str, ModelDescriptor] = {}
        self._load()

    @classmethod
    def get_instance(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = ModelRegistry()
        return cls._instance

    def _load(self):
        models = self._db.load_all()
        self._models = {m.id: m for m in models}
        logger.info(f"ModelRegistry: Loaded {len(self._models)} model(s) from registry.")

    def register(self, descriptor: ModelDescriptor) -> ModelDescriptor:
        """Add a new model to the registry and persist immediately."""
        self._models[descriptor.id] = descriptor
        self._persist()
        logger.info(f"ModelRegistry: Registered model '{descriptor.display_name}' ({descriptor.id})")
        return descriptor

    def remove(self, model_id: str) -> bool:
        """Remove a model by ID. Returns True if removed."""
        if model_id in self._models:
            name = self._models[model_id].display_name
            del self._models[model_id]
            self._persist()
            logger.info(f"ModelRegistry: Removed model '{name}' ({model_id})")
            return True
        return False

    def get(self, model_id: str) -> Optional[ModelDescriptor]:
        return self._models.get(model_id)

    def get_all(self) -> List[ModelDescriptor]:
        return list(self._models.values())

    def get_managed_models_dir(self) -> str:
        """Returns the absolute path to the managed model storage directory."""
        os.makedirs(_MODELS_DIR, exist_ok=True)
        return os.path.abspath(_MODELS_DIR)

    def _persist(self):
        self._db.save_all(list(self._models.values()))
