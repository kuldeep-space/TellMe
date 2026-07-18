"""
Model Loader.

Responsible for translating a model's runtime configuration into the
specific parameters required by the active inference backend.
"""

from backend.domain.model_registration import ModelRegistration


class ModelLoader:
    """
    Prepares a registered model for inference.

    This class abstracts the complex logic of converting agnostic runtime
    configurations (e.g., gpu_layers, threads) into backend-specific
    loading kwargs.
    """

    def load(self, model: ModelRegistration) -> bool:
        """
        Load the model into the active inference backend.

        Args:
            model: The registered model to load.

        Returns:
            True if successful.

        Raises:
            ModelLoadError: If loading fails.
        """
        # In a real implementation, this would dispatch to the ILLMProvider
        return True
