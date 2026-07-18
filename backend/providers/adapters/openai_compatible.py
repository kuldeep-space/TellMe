from typing import Any, List, TYPE_CHECKING
from backend.domain.provider import (
    AIProvider, ProviderMetadata, ProviderCategory, ProviderType,
    ProviderCapability, ConfigurationSchema, SchemaField, FieldType,
    RuntimeParameterSchema
)

if TYPE_CHECKING:
    from backend.domain.models import ProviderAction, InferenceRequest
    from backend.domain.provider import ProviderConfiguration


class OpenAICompatibleProvider(AIProvider):
    @classmethod
    def get_metadata(cls) -> ProviderMetadata:
        return ProviderMetadata(
            id="openai_compatible",
            display_name="OpenAI Compatible",
            category=ProviderCategory.OPENAI_COMPATIBLE,
            description="Connect to any provider implementing the OpenAI API (e.g. LocalAI, OpenRouter, Together, DeepSeek).",
            icon="openai.svg"
        )
        
    def get_capabilities(self) -> ProviderCapability:
        return ProviderCapability(
            supports_streaming=True,
            supports_json_mode=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_system_prompts=True,
            max_context_length=128000,
            max_output_tokens=4096
        )
        
    def get_config_schema(self) -> ConfigurationSchema:
        return ConfigurationSchema(fields=[
            SchemaField(id="base_url", label="Base URL", type=FieldType.TEXT, default="https://api.openai.com/v1"),
            SchemaField(id="api_key", label="API Key", type=FieldType.PASSWORD, description="Leave blank if not required by the endpoint."),
            SchemaField(id="model", label="Model ID", type=FieldType.TEXT, default="gpt-4o"),
        ])
        
    def get_runtime_schema(self) -> RuntimeParameterSchema:
        return RuntimeParameterSchema(
            supports_temperature=True,
            supports_top_p=True,
            supports_top_k=False,
            supports_min_p=False,
            supports_typical_p=False,
            supports_repeat_penalty=True,
            supports_frequency_penalty=True,
            supports_presence_penalty=True,
            supports_seed=True,
            supports_stop_sequences=True,
            supports_max_tokens=True,
            supports_context_length=False,
            supports_reasoning_effort=False
        )

    def get_supported_actions(self) -> List['ProviderAction']:
        from backend.domain.models import ProviderAction
        return [
            ProviderAction(id="health_check", display_name="Health Check", description="Verify API connectivity", icon="activity.svg"),
            ProviderAction(id="refresh_models", display_name="Refresh Models", description="Query the /v1/models endpoint", icon="refresh.svg")
        ]
        
    def execute_action(self, action_id: str, config: 'ProviderConfiguration') -> Any:
        from backend.domain.models import HealthStatus, ModelInfo, ProviderError
        import time
        if action_id == "health_check":
            # Simulate a quick network call
            time.sleep(1)
            return HealthStatus(success=True, status="OK", message="Successfully connected to endpoint", latency=125.0)
        elif action_id == "refresh_models":
            time.sleep(2)
            # Simulated model discovery
            return [
                ModelInfo(id="gpt-4o", display_name="GPT-4o", provider="openai_compatible"),
                ModelInfo(id="gpt-4o-mini", display_name="GPT-4o Mini", provider="openai_compatible")
            ]
        raise ProviderError(f"Unsupported action: {action_id}")
        
    def stream_generate(self, request: 'InferenceRequest') -> Any:
        from backend.domain.events import GenerationStarted, TokenReceived, GenerationCompleted, GenerationFailed
        import time
        
        yield GenerationStarted(session_id=request.session_id, model=request.parameters.get("model", "unknown"))
        
        # Simulate text stream
        text = f"This is a simulated response from {self.get_metadata().display_name} for the prompt: '{request.user_prompt}'\n"
        words = text.split(" ")
        
        for word in words:
            time.sleep(0.05)
            yield TokenReceived(text=word + " ")
            
        yield GenerationCompleted(finish_reason="stop", usage={"prompt": 10, "completion": len(words)}, latency=len(words) * 0.05)
