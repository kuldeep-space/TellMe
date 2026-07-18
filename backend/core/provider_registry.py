"""
Core Service: Provider Registry & Factory.

Manages the registration and instantiation of AI providers (both local and API).
"""
from typing import Dict, List, Type
from backend.domain.provider import AIProvider, ProviderType, ProviderCapability, ConfigurationSchema, SchemaField, FieldType

class ProviderFactory:
    """Instantiates providers based on their registered class."""
    
    _providers: Dict[str, Type[AIProvider]] = {}
    
    @classmethod
    def register(cls, provider_class: Type[AIProvider]):
        cls._providers[provider_class().id] = provider_class
        
    @classmethod
    def create(cls, provider_id: str) -> AIProvider:
        if provider_id not in cls._providers:
            raise ValueError(f"Unknown provider ID: {provider_id}")
        return cls._providers[provider_id]()
        
    @classmethod
    def get_all_classes(cls) -> List[Type[AIProvider]]:
        return list(cls._providers.values())


class ProviderRegistry:
    """
    Registry for querying available providers.
    The UI uses this to populate dropdowns and dynamic forms.
    """
    
    @staticmethod
    def get_providers() -> List[AIProvider]:
        """Returns instantiated instances of all registered providers."""
        return [cls() for cls in ProviderFactory.get_all_classes()]
        
    @staticmethod
    def get_provider(provider_id: str) -> AIProvider:
        return ProviderFactory.create(provider_id)


# --- Example Implementations (To be expanded in the future) ---

class LlamaCppProvider(AIProvider):
    @property
    def id(self) -> str: return "llama_cpp"
    @property
    def name(self) -> str: return "llama.cpp (Local)"
    @property
    def provider_type(self) -> ProviderType: return ProviderType.LOCAL

    def get_capabilities(self) -> ProviderCapability:
        return ProviderCapability(
            supports_streaming=True,
            supports_json_mode=True,
            max_context_length=8192,
            max_output_tokens=4096
        )
        
    def get_config_schema(self) -> ConfigurationSchema:
        return ConfigurationSchema(fields=[
            SchemaField(id="model_path", label="Installed Model", type=FieldType.SELECT, options=["auto", "Llama-3-8B-Instruct.Q4_K_M.gguf"]),
        ])

class OpenAIProvider(AIProvider):
    @property
    def id(self) -> str: return "openai"
    @property
    def name(self) -> str: return "OpenAI API"
    @property
    def provider_type(self) -> ProviderType: return ProviderType.API

    def get_capabilities(self) -> ProviderCapability:
        return ProviderCapability(
            supports_streaming=True,
            supports_json_mode=True,
            supports_function_calling=True,
            supports_vision=True,
            max_context_length=128000,
            max_output_tokens=4096
        )
        
    def get_config_schema(self) -> ConfigurationSchema:
        return ConfigurationSchema(fields=[
            SchemaField(id="base_url", label="Base URL", type=FieldType.TEXT, default="https://api.openai.com/v1"),
            SchemaField(id="api_key", label="API Key", type=FieldType.PASSWORD),
            SchemaField(id="model", label="Model", type=FieldType.TEXT, default="gpt-4o"),
        ])

class GeminiProvider(AIProvider):
    @property
    def id(self) -> str: return "gemini"
    @property
    def name(self) -> str: return "Google Gemini API"
    @property
    def provider_type(self) -> ProviderType: return ProviderType.API

    def get_capabilities(self) -> ProviderCapability:
        return ProviderCapability(
            supports_streaming=True,
            supports_json_mode=True,
            supports_function_calling=True,
            supports_vision=True,
            max_context_length=2000000,
            max_output_tokens=8192
        )
        
    def get_config_schema(self) -> ConfigurationSchema:
        return ConfigurationSchema(fields=[
            SchemaField(id="api_key", label="API Key", type=FieldType.PASSWORD),
            SchemaField(id="model", label="Model", type=FieldType.TEXT, default="gemini-1.5-pro"),
        ])


# Register the default providers
ProviderFactory.register(LlamaCppProvider)
ProviderFactory.register(OpenAIProvider)
ProviderFactory.register(GeminiProvider)
