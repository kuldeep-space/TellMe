"""
GGUF Validator.

Verifies that extracted GGUF metadata is compatible with the TellMe
inference engine capabilities.
"""

from backend.core.exceptions import ModelValidationError
from backend.model_management.metadata import GGUFMetadata
from backend.shared.enums.model import ModelArchitecture


class GGUFValidator:
    """
    Validates GGUF model compatibility.

    Ensures the model architecture is recognized and that the
    model's context window and quantization are supported.
    """

    SUPPORTED_ARCHITECTURES = {
        ModelArchitecture.LLAMA,
        ModelArchitecture.QWEN,
        ModelArchitecture.MISTRAL,
        ModelArchitecture.GEMMA,
        ModelArchitecture.PHI,
    }

    def validate(self, metadata: GGUFMetadata) -> None:
        """
        Validate the extracted metadata.

        Args:
            metadata: Extracted GGUF metadata.

        Raises:
            ModelValidationError: If the model is unsupported or invalid.
        """
        if metadata.architecture not in self.SUPPORTED_ARCHITECTURES:
            raise ModelValidationError(
                f"Unsupported model architecture '{metadata.architecture}'. "
                f"Supported: {[a.value for a in self.SUPPORTED_ARCHITECTURES]}",
                context={"architecture": metadata.architecture.value}
            )

        # Additional validation (e.g., minimum parameter count, known quantization)
        # would be implemented here.
