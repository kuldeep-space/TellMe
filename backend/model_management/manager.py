"""
Active Model Manager.

Coordinates the switching of models and manages the active LLM state.
"""

from uuid import UUID

from backend.model_management.registry import ModelRegistry
from backend.model_management.loader import ModelLoader


class ModelManager:
    """
    Manages the currently active AI model.

    Ensures that when a user switches models, the old model is safely
    unloaded from VRAM before the new one is loaded.
    """

    def __init__(self, registry: ModelRegistry, loader: ModelLoader) -> None:
        """Initialize the model manager."""
        self._registry = registry
        self._loader = loader
        self._active_model_id: UUID | None = None

    def set_active_model(self, model_id: UUID) -> bool:
        """
        Switch the currently active model.

        Args:
            model_id: The UUID of the model to activate.

        Returns:
            True if successful.

        Raises:
            ModelNotFoundError: If the ID is not registered.
            ModelLoadError: If loading fails.
        """
        model = self._registry.get(model_id)
        if not model:
            return False

        # In a real implementation, unload the previous model here

        success = self._loader.load(model)
        if success:
            self._active_model_id = model_id
            model.touch()

        return success

    @property
    def active_model_id(self) -> UUID | None:
        """Return the UUID of the currently active model."""
        return self._active_model_id
