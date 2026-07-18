from backend.domain.provider import (
    AIProvider, ProviderMetadata, ProviderCategory, ProviderType,
    ProviderCapability, ConfigurationSchema, SchemaField, FieldType,
    RuntimeParameterSchema
)

class AnthropicProvider(AIProvider):
    @classmethod
    def get_metadata(cls) -> ProviderMetadata:
        return ProviderMetadata(
            id="anthropic",
            display_name="Anthropic Claude",
            category=ProviderCategory.NATIVE,
            description="Native support for Claude models via the Anthropic API.",
            icon="anthropic.svg"
        )
        
    def get_capabilities(self) -> ProviderCapability:
        return ProviderCapability(
            supports_streaming=True,
            supports_json_mode=True,
            supports_function_calling=True,
            supports_vision=True,
            max_context_length=200000,
            max_output_tokens=4096
        )
        
    def get_config_schema(self) -> ConfigurationSchema:
        return ConfigurationSchema(fields=[
            SchemaField(id="api_key", label="API Key", type=FieldType.PASSWORD),
            SchemaField(id="model", label="Model ID", type=FieldType.TEXT, default="claude-3-5-sonnet-20240620"),
        ])
        
    def get_runtime_schema(self) -> RuntimeParameterSchema:
        return RuntimeParameterSchema(
            supports_temperature=True,
            supports_top_p=True,
            supports_top_k=True,
            supports_max_tokens=True,
            supports_stop_sequences=True,
            # Claude does not typically expose presence/frequency penalties directly
            supports_frequency_penalty=False,
            supports_presence_penalty=False,
            supports_repeat_penalty=False
        )

class GeminiProvider(AIProvider):
    @classmethod
    def get_metadata(cls) -> ProviderMetadata:
        return ProviderMetadata(
            id="gemini",
            display_name="Google Gemini",
            category=ProviderCategory.NATIVE,
            description="Native support for Google Gemini models.",
            icon="google.svg"
        )
        
    def get_capabilities(self) -> ProviderCapability:
        return ProviderCapability(
            supports_streaming=True,
            supports_json_mode=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_audio_in=True,
            max_context_length=2000000,
            max_output_tokens=8192
        )
        
    def get_config_schema(self) -> ConfigurationSchema:
        return ConfigurationSchema(fields=[
            SchemaField(id="api_key", label="API Key", type=FieldType.PASSWORD),
            SchemaField(id="model", label="Model ID", type=FieldType.TEXT, default="gemini-1.5-pro"),
        ])
        
    def get_runtime_schema(self) -> RuntimeParameterSchema:
        return RuntimeParameterSchema(
            supports_temperature=True,
            supports_top_p=True,
            supports_top_k=True,
            supports_max_tokens=True,
            supports_stop_sequences=True,
            supports_presence_penalty=True,
            supports_frequency_penalty=True
        )
