import os
import logging
from backend.domain.models import ModelDescriptor
from backend.core.runtime.models import EngineCapabilities
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)

class RuntimeValidator:
    """Validates prerequisites before allowing the engine to load a model."""
    
    @staticmethod
    def validate(descriptor: ModelDescriptor, capabilities: EngineCapabilities, available_ram_mb: float):
        if not os.path.isfile(descriptor.path):
            raise FileNotFoundError(f"Model file not found: {descriptor.path}")
            
        if not os.access(descriptor.path, os.R_OK):
            raise PermissionError(f"Model file is not readable: {descriptor.path}")
            
        model_size_mb = os.path.getsize(descriptor.path) / (1024 * 1024)
        
        settings = get_settings()
        allow_unsafe = getattr(settings, "allow_unsafe_loading", False)
        
        if model_size_mb > available_ram_mb:
            if not allow_unsafe:
                raise MemoryError(f"Insufficient RAM. Model size ({model_size_mb:.1f} MB) exceeds available RAM ({available_ram_mb:.1f} MB).")
            else:
                logger.warning(
                    f"Model size ({model_size_mb:.1f} MB) exceeds available RAM ({available_ram_mb:.1f} MB). "
                    "allow_unsafe_loading is enabled, attempting to load anyway."
                )
            
        # Add capability validation based on descriptor requirements if necessary
        # Example: if descriptor.format == ModelFormat.GGUF and not capabilities.supports_mmap: ...
        
        return True

