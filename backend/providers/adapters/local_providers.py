from typing import Any, TYPE_CHECKING
from backend.domain.provider import (
    AIProvider, ProviderMetadata, ProviderCategory, ProviderType,
    ProviderCapability, ConfigurationSchema, SchemaField, FieldType,
    RuntimeParameterSchema
)

if TYPE_CHECKING:
    from backend.domain.models import ProviderAction, InferenceRequest
    from backend.domain.provider import ProviderConfiguration

class LlamaCppProvider(AIProvider):
    @classmethod
    def get_metadata(cls) -> ProviderMetadata:
        return ProviderMetadata(
            id="llama_cpp",
            display_name="llama.cpp",
            category=ProviderCategory.LOCAL,
            description="Native bindings for llama.cpp local inference.",
            icon="llama.svg"
        )
        
    def get_capabilities(self) -> ProviderCapability:
        return ProviderCapability(
            supports_streaming=True,
            supports_json_mode=True,
            supports_function_calling=True,
            max_context_length=32768,
            max_output_tokens=4096
        )
        
    def get_config_schema(self) -> ConfigurationSchema:
        return ConfigurationSchema(fields=[
            SchemaField(id="model_path", label="Model Path / Name", type=FieldType.FILE_PATH, default=""),
        ])
        
    def get_runtime_schema(self) -> RuntimeParameterSchema:
        return RuntimeParameterSchema(
            supports_temperature=True,
            supports_top_p=True,
            supports_top_k=True,
            supports_min_p=True,
            supports_typical_p=True,
            supports_repeat_penalty=True,
            supports_frequency_penalty=True,
            supports_presence_penalty=True,
            supports_seed=True,
            supports_stop_sequences=True,
            supports_max_tokens=True,
            supports_context_length=False,
            supports_gpu_layers=True
        )

    def get_supported_actions(self) -> list['ProviderAction']:
        from backend.domain.models import ProviderAction
        return [
            ProviderAction(id="health_check", display_name="Engine Status", description="Check llama.cpp health", icon="activity.svg"),
            ProviderAction(id="load_model", display_name="Load Model", description="Load weights into VRAM", icon="download.svg"),
            ProviderAction(id="unload_model", display_name="Unload Model", description="Clear VRAM", icon="trash.svg", dangerous=True)
        ]
        
    def execute_action(self, action_id: str, config: 'ProviderConfiguration') -> Any:
        from backend.domain.models import HealthStatus, ProviderError
        import time
        if action_id == "health_check":
            time.sleep(0.5)
            return HealthStatus(success=True, status="Ready", message="llama.cpp is idle", latency=0.0)
        elif action_id == "load_model":
            time.sleep(1)
            return True
        elif action_id == "unload_model":
            time.sleep(1)
            return True
        raise ProviderError(f"Unsupported action: {action_id}")
        
    def stream_generate(self, request: 'InferenceRequest') -> Any:
        from backend.domain.events import GenerationStarted, TokenReceived, GenerationCompleted
        import time
        yield GenerationStarted(session_id=request.session_id, model=request.parameters.get("model", "local"))
        text = f"Local llama.cpp inference stream responding to: {request.user_prompt}\n"
        words = text.split(" ")
        for word in words:
            time.sleep(0.02)
            yield TokenReceived(text=word + " ")
        yield GenerationCompleted(finish_reason="stop", usage={"prompt": 5, "completion": len(words)}, latency=len(words) * 0.02)
class OllamaProvider(AIProvider):
    @classmethod
    def get_metadata(cls) -> ProviderMetadata:
        return ProviderMetadata(
            id="ollama",
            display_name="Ollama (Native)",
            category=ProviderCategory.LOCAL,
            description="Connect directly to a local Ollama instance via native API.",
            icon="ollama.svg"
        )
        
    def get_capabilities(self) -> ProviderCapability:
        return ProviderCapability(
            supports_streaming=True,
            supports_json_mode=True,
            supports_function_calling=True,
            max_context_length=32768,
            max_output_tokens=4096
        )
        
    def get_config_schema(self) -> ConfigurationSchema:
        return ConfigurationSchema(fields=[
            SchemaField(id="host", label="Ollama Host", type=FieldType.TEXT, default="http://localhost:11434"),
            SchemaField(id="model", label="Model Name", type=FieldType.TEXT, default="llama3"),
        ])
        
    def get_runtime_schema(self) -> RuntimeParameterSchema:
        return RuntimeParameterSchema(
            supports_temperature=True,
            supports_top_p=True,
            supports_top_k=True,
            supports_repeat_penalty=True,
            supports_seed=True,
            supports_stop_sequences=True,
            supports_max_tokens=True,
            supports_context_length=True,
            supports_gpu_layers=True
        )

    def get_supported_actions(self) -> list['ProviderAction']:
        from backend.domain.models import ProviderAction
        return [
            ProviderAction(id="health_check", display_name="Ollama Status", description="Check if Ollama daemon is running", icon="activity.svg"),
            ProviderAction(id="load_model", display_name="Load Model", description="Pre-load into VRAM", icon="download.svg"),
            ProviderAction(id="unload_model", display_name="Unload Model", description="Free VRAM", icon="trash.svg", dangerous=True)
        ]
        
    def execute_action(self, action_id: str, config: 'ProviderConfiguration') -> Any:
        from backend.domain.models import HealthStatus, ProviderError
        import time
        if action_id == "health_check":
            time.sleep(0.5)
            return HealthStatus(success=True, status="Running", message="Ollama daemon is active", latency=20.0)
        elif action_id == "load_model" or action_id == "unload_model":
            time.sleep(1)
            return True
        raise ProviderError(f"Unsupported action: {action_id}")
        
    def stream_generate(self, request: 'InferenceRequest') -> Any:
        from backend.domain.events import GenerationStarted, TokenReceived, GenerationCompleted
        import time
        yield GenerationStarted(session_id=request.session_id, model=request.parameters.get("model", "ollama"))
        text = f"Ollama streaming response for prompt: {request.user_prompt}\n"
        words = text.split(" ")
        for word in words:
            time.sleep(0.02)
            yield TokenReceived(text=word + " ")
        yield GenerationCompleted(finish_reason="stop", usage={"prompt": 5, "completion": len(words)}, latency=len(words) * 0.02)
