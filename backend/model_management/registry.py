"""
Model Registry.

Maintains the database of all user-registered local AI models.
"""

from collections.abc import Sequence
from uuid import UUID

from backend.domain.model_registration import ModelRegistration


class ModelRegistry:
    """
    In-memory or persistent registry for all registered AI models.

    This acts as a dedicated repository specifically for the active
    catalog of LLMs available to the user.
    """

    def __init__(self) -> None:
        """Initialize the registry."""
        self._models: dict[UUID, ModelRegistration] = {}

    def register(self, model: ModelRegistration) -> None:
        """
        Add a new model to the registry.

        Args:
            model: The validated ModelRegistration entity.
        """
        self._models[model.model_id] = model

    def get(self, model_id: UUID) -> ModelRegistration | None:
        """
        Retrieve a registered model by its ID.

        Args:
            model_id: The unique UUID of the model.

        Returns:
            The ModelRegistration if found, None otherwise.
        """
        return self._models.get(model_id)

    def list_all(self) -> Sequence[ModelRegistration]:
        """
        List all registered models.

        Returns:
            A sequence of all registered ModelRegistration entities.
        """
        return list(self._models.values())

    def unregister(self, model_id: UUID) -> bool:
        """
        Remove a model from the registry.

        Args:
            model_id: The unique UUID of the model to remove.

        Returns:
            True if removed, False if not found.
        """
        if model_id in self._models:
            del self._models[model_id]
            return True
        return False
