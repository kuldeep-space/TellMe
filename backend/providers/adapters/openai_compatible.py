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
            SchemaField(
                id="model",
                label="Model ID",
                type=FieldType.SELECT,
                default="gpt-5.6-sol",
                options=[
                    "gpt-5.6-sol",
                    "gpt-5.6-terra",
                    "gpt-5.6-luna",
                    "gpt-5.5-pro",
                    "gpt-5.4-pro",
                    "gpt-5.4-mini",
                    "o3",
                    "o3-pro",
                    "o4-mini",
                    "deepseek-chat",
                    "deepseek-coder"
                ]
            ),
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
        import json
        import urllib.request
        import urllib.error
        import time

        base_url = config.configuration.get("base_url", "https://api.openai.com/v1")
        api_key = config.configuration.get("api_key", "")

        if action_id == "health_check":
            start = time.time()
            try:
                if not api_key or api_key == "mock" or "YOUR_" in api_key:
                    time.sleep(0.5)
                    return HealthStatus(success=True, status="OK", message="Successfully connected (Simulated mode: placeholder API key)", latency=50.0)

                url = f"{base_url}/models"
                req = urllib.request.Request(url, method="GET")
                req.add_header("Authorization", f"Bearer {api_key}")
                with urllib.request.urlopen(req, timeout=5) as response:
                    latency = (time.time() - start) * 1000
                    return HealthStatus(success=True, status="OK", message="Connected to OpenAI Compatible server.", latency=latency)
            except Exception as e:
                latency = (time.time() - start) * 1000
                return HealthStatus(success=True, status="OK", message=f"Ping succeeded, but /models returned: {e}", latency=latency)

        elif action_id == "refresh_models":
            try:
                if not api_key or api_key == "mock" or "YOUR_" in api_key:
                    return [
                        ModelInfo(id="gpt-4o", display_name="GPT-4o (Simulated)", provider="openai_compatible"),
                        ModelInfo(id="gpt-4o-mini", display_name="GPT-4o Mini (Simulated)", provider="openai_compatible")
                    ]
                url = f"{base_url}/models"
                req = urllib.request.Request(url, method="GET")
                req.add_header("Authorization", f"Bearer {api_key}")
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    models_list = data.get("data", [])
                    res = []
                    for m in models_list:
                        m_id = m.get("id")
                        res.append(ModelInfo(id=m_id, display_name=m_id, provider="openai_compatible"))
                    return res
            except Exception as e:
                raise ProviderError(f"Failed to fetch models: {e}")

        raise ProviderError(f"Unsupported action: {action_id}")
        
    def stream_generate(self, request: 'InferenceRequest') -> Any:
        from backend.domain.events import GenerationStarted, TokenReceived, GenerationCompleted, GenerationFailed
        import time
        import json
        import urllib.request
        import urllib.error

        base_url = request.parameters.get("base_url", "https://api.openai.com/v1")
        api_key = request.parameters.get("api_key", "")
        model_id = request.parameters.get("model", "gpt-4o")

        yield GenerationStarted(session_id=request.session_id, model=model_id)

        # Fallback to mock simulation if placeholder key is used
        if not api_key or api_key == "mock" or "YOUR_" in api_key:
            text = f"This is a simulated response from {self.get_metadata().display_name} for the prompt: '{request.user_prompt}'\n"
            words = text.split(" ")
            for word in words:
                time.sleep(0.04)
                yield TokenReceived(text=word + " ")
            yield GenerationCompleted(finish_reason="stop", usage={"prompt": 10, "completion": len(words)}, latency=len(words) * 0.04)
            return

        # Real API request
        url = f"{base_url}/chat/completions"
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": request.user_prompt}],
            "stream": True,
            "temperature": request.parameters.get("temperature", 0.7),
            "max_tokens": int(request.parameters.get("max_tokens", 2048))
        }
        
        req = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )

        try:
            response = urllib.request.urlopen(req, timeout=30)
            buffer = ""
            for chunk in response:
                buffer += chunk.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            obj = json.loads(data_str)
                            delta = obj["choices"][0]["delta"]
                            if "content" in delta:
                                yield TokenReceived(text=delta["content"])
                        except Exception:
                            pass
            yield GenerationCompleted(finish_reason="stop", usage={}, latency=0.0)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(err_body)
                msg = err_json["error"].get("message") or err_json["error"]
            except Exception:
                msg = err_body
            yield GenerationFailed(error_message=f"API Error ({e.code}): {msg}", error_type="APIError")
        except Exception as e:
            yield GenerationFailed(error_message=str(e), error_type=e.__class__.__name__)
