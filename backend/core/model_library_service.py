"""
Core Service: Model Library Service.

Orchestrates the full model import pipeline:
    Validate -> Extract Metadata -> Compatibility Check -> Register -> Ready

This is the single entry point for all model management operations.
The registry, extractor, and resolver are each kept focused on their own concern.
"""
import os
import shutil
import logging
from dataclasses import dataclass
from typing import Optional
from backend.domain.models import ModelDescriptor, ModelFormat
from backend.core.model_registry import ModelRegistry
from backend.core.metadata_extractor import extract_metadata
from backend.core.engine_resolver import EngineResolver

logger = logging.getLogger(__name__)

# Supported file extensions (mapped to ModelFormat)
_SUPPORTED_EXTENSIONS = {
    ".gguf":         ModelFormat.GGUF,
    ".ggml":         ModelFormat.GGML,
    ".safetensors":  ModelFormat.SAFETENSORS,
    ".onnx":         ModelFormat.ONNX,
}


@dataclass
class ImportResult:
    """Result returned after attempting to import a model."""
    success: bool
    descriptor: Optional[ModelDescriptor] = None
    error: str = ""
    compatible_engine: str = ""

    @property
    def display_message(self) -> str:
        if self.success and self.descriptor:
            return (
                f"✓ '{self.descriptor.display_name}' imported successfully.\n"
                f"  Engine: {self.compatible_engine}  |  "
                f"Format: {self.descriptor.format.value.upper()}  |  "
                f"Size: {self._format_size(self.descriptor.size_bytes)}"
            )
        return f"✗ Import failed: {self.error}"

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes >= 1_073_741_824:
            return f"{size_bytes / 1_073_741_824:.1f} GB"
        if size_bytes >= 1_048_576:
            return f"{size_bytes / 1_048_576:.1f} MB"
        return f"{size_bytes / 1024:.1f} KB"


class ModelLibraryService:
    """
    Orchestrates the consumer-facing model import workflow.
    Does NOT manage persistence or VRAM directly — those are registry and runtime concerns.
    """

    def __init__(self, registry: Optional[ModelRegistry] = None):
        self._registry = registry or ModelRegistry.get_instance()

    # ------------------------------------------------------------------
    # Import pipeline
    # ------------------------------------------------------------------

    def import_model(self, source_path: str, copy_to_library: bool = True) -> ImportResult:
        """
        Full import pipeline. Called from the UI "Import Model" button.

        Steps:
        1. Validate file exists and format is supported.
        2. Extract metadata from file headers + filename heuristics.
        3. Check compatibility against registered engines.
        4. Optionally copy to managed library directory.
        5. Register in ModelRegistry.
        6. Return ImportResult with summary.
        """
        # --- Step 1: Validate ---
        if not os.path.isfile(source_path):
            return ImportResult(success=False, error=f"File not found: {source_path}")

        ext = os.path.splitext(source_path)[1].lower()
        if ext not in _SUPPORTED_EXTENSIONS:
            supported = ", ".join(_SUPPORTED_EXTENSIONS.keys())
            return ImportResult(
                success=False,
                error=f"Unsupported format '{ext}'. Supported: {supported}"
            )

        # Check for duplicates (same path already registered)
        dest_dir = self._registry.get_managed_models_dir()
        filename = os.path.basename(source_path)
        dest_path = os.path.join(dest_dir, filename)
        
        for existing in self._registry.get_all():
            if os.path.abspath(existing.path) == os.path.abspath(source_path) or (copy_to_library and os.path.abspath(existing.path) == os.path.abspath(dest_path)):
                return ImportResult(
                    success=False,
                    error=f"Model is already imported and available in your library as '{existing.display_name}'"
                )

        # --- Step 2: Extract Metadata ---
        try:
            descriptor = extract_metadata(source_path)
        except Exception as e:
            return ImportResult(success=False, error=f"Metadata extraction failed: {e}")

        # --- Step 3: Compatibility Check ---
        engine_id = EngineResolver.resolve(descriptor)
        if not engine_id:
            available = [c.display_name for c in EngineResolver.get_available_engines()]
            if not available:
                msg = (
                    "No inference engines are installed. "
                    "For GGUF models, install llama-cpp-python:\n"
                    "  pip install llama-cpp-python"
                )
            else:
                msg = (
                    f"No installed engine supports '{descriptor.format.value.upper()}' format "
                    f"with architecture '{descriptor.architecture}'. "
                    f"Available engines: {', '.join(available)}."
                )
            return ImportResult(success=False, error=msg)

        # --- Step 4: Copy to Managed Library (optional) ---
        final_path = source_path
        if copy_to_library:
            final_path = self._copy_to_library(source_path, descriptor)

        descriptor.path = final_path

        # --- Step 5: Register ---
        try:
            self._registry.register(descriptor)
        except Exception as e:
            if copy_to_library and final_path != source_path and os.path.exists(final_path):
                try:
                    os.remove(final_path)
                    logger.info(f"ModelLibraryService: Rolled back file '{final_path}' due to registry failure.")
                except Exception as rollback_err:
                    logger.error(f"ModelLibraryService: Failed to rollback file '{final_path}': {rollback_err}")
            return ImportResult(success=False, error=f"Registration failed: {e}")

        logger.info(f"ModelLibraryService: Import complete for '{descriptor.display_name}'.")
        return ImportResult(
            success=True,
            descriptor=descriptor,
            compatible_engine=engine_id,
        )

    # ------------------------------------------------------------------
    # Removal
    # ------------------------------------------------------------------

    def remove_model(self, model_id: str, delete_file: bool = False) -> bool:
        """Remove a model from the registry. Optionally delete the file."""
        descriptor = self._registry.get(model_id)
        if not descriptor:
            return False

        if delete_file and os.path.exists(descriptor.path):
            try:
                os.remove(descriptor.path)
                logger.info(f"ModelLibraryService: Deleted file '{descriptor.path}'")
            except Exception as e:
                logger.warning(f"ModelLibraryService: Could not delete file: {e}")

        return self._registry.remove(model_id)

    # ------------------------------------------------------------------
    # Re-scan
    # ------------------------------------------------------------------

    def rescan_library(self):
        """Remove registry entries whose files no longer exist on disk."""
        stale = [m for m in self._registry.get_all() if not os.path.exists(m.path)]
        for m in stale:
            logger.info(f"ModelLibraryService: Removing stale entry '{m.display_name}'.")
            self._registry.remove(m.id)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _copy_to_library(self, source_path: str, descriptor: ModelDescriptor) -> str:
        """Copy the model file into the managed models directory."""
        dest_dir = self._registry.get_managed_models_dir()
        filename = os.path.basename(source_path)
        dest_path = os.path.join(dest_dir, filename)

        if os.path.abspath(source_path) == os.path.abspath(dest_path):
            return dest_path  # Already in library

        os.makedirs(dest_dir, exist_ok=True)
        logger.info(f"ModelLibraryService: Copying '{filename}' to managed library...")
        shutil.copy2(source_path, dest_path)
        logger.info(f"ModelLibraryService: Copy complete → '{dest_path}'")
        return dest_path
