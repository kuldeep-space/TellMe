"""
Core Service: Provider Registry.

Manages the registration and instantiation of AI providers (both local and API).
Automatically discovers providers that inherit from AIProvider via __init_subclass__.
"""
from typing import Dict, List, Type
import importlib
import pkgutil
from backend.domain.provider import AIProvider, ProviderCategory

class ProviderRegistry:
    """
    Registry for querying available providers.
    The UI uses this to populate dropdowns and dynamic forms.
    """
    
    @classmethod
    def load_adapters(cls):
        """Dynamically loads all modules in the adapters package to trigger registration."""
        try:
            import backend.providers.adapters as adapters
            for _, name, _ in pkgutil.iter_modules(adapters.__path__):
                importlib.import_module(f"backend.providers.adapters.{name}")
        except ModuleNotFoundError:
            pass # Adapters folder might not exist yet
    
    @classmethod
    def get_providers(cls) -> List[AIProvider]:
        """Returns instantiated instances of all registered providers."""
        cls.load_adapters()
        return [cls_type() for cls_type in AIProvider._registry.values()]
        
    @classmethod
    def get_providers_by_category(cls, category: ProviderCategory) -> List[AIProvider]:
        """Returns providers filtered by their category."""
        return [p for p in cls.get_providers() if p.get_metadata().category == category]
        
    @classmethod
    def get_provider(cls, provider_id: str) -> AIProvider:
        """Instantiates and returns a specific provider by its ID."""
        cls.load_adapters()
        # Find the class where get_metadata().id == provider_id
        for cls_type in AIProvider._registry.values():
            if cls_type.get_metadata().id == provider_id:
                return cls_type()
        raise ValueError(f"Unknown provider ID: {provider_id}")
