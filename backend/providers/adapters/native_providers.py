from typing import Any, List, TYPE_CHECKING
from backend.domain.provider import (
    AIProvider, ProviderMetadata, ProviderCategory, ProviderType,
    ProviderCapability, ConfigurationSchema, SchemaField, FieldType,
    RuntimeParameterSchema
)

if TYPE_CHECKING:
    from backend.domain.models import ProviderAction, InferenceRequest
    from backend.domain.provider import ProviderConfiguration

class AnthropicProvider(AIProvider):
    @classmethod
    def get_metadata(cls) -> ProviderMetadata:
        return ProviderMetadata(
            id="anthropic",
            display_name="Anthropic Claude",
            category=ProviderCategory.NATIVE,
            description="Official integration with Anthropic's Claude models.",
            icon="anthropic.svg"
        )
        
    def get_capabilities(self) -> ProviderCapability:
        return ProviderCapability(
            supports_streaming=True,
            supports_json_mode=False,
            supports_function_calling=True,
            supports_vision=True,
            supports_system_prompts=True,
            max_context_length=200000,
            max_output_tokens=4096
        )
        
    def get_config_schema(self) -> ConfigurationSchema:
        return ConfigurationSchema(fields=[
            SchemaField(id="base_url", label="Base URL", type=FieldType.TEXT, default="https://api.anthropic.com"),
            SchemaField(id="api_key", label="API Key", type=FieldType.PASSWORD),
            SchemaField(
                id="model",
                label="Model ID",
                type=FieldType.SELECT,
                default="claude-sonnet-5",
                options=[
                    "claude-sonnet-5",
                    "claude-fable-5",
                    "claude-opus-4-8",
                    "claude-haiku-4-5-20251001"
                ]
            ),
        ])
        
    def get_runtime_schema(self) -> RuntimeParameterSchema:
        return RuntimeParameterSchema(
            supports_temperature=True,
            supports_top_p=True,
            supports_top_k=True,
            supports_max_tokens=True,
            supports_stop_sequences=True,
            supports_frequency_penalty=False,
            supports_presence_penalty=False,
            supports_repeat_penalty=False
        )

    def get_supported_actions(self) -> List['ProviderAction']:
        from backend.domain.models import ProviderAction
        return [
            ProviderAction(id="health_check", display_name="Health Check", description="Verify API connectivity", icon="activity.svg")
        ]
        
    def execute_action(self, action_id: str, config: 'ProviderConfiguration') -> Any:
        from backend.domain.models import HealthStatus, ProviderError
        import json
        import urllib.request
        import urllib.error
        import time

        base_url = config.configuration.get("base_url", "https://api.anthropic.com")
        api_key = config.configuration.get("api_key", "")

        if action_id == "health_check":
            start = time.time()
            try:
                if not api_key or api_key == "mock" or "YOUR_" in api_key:
                    time.sleep(0.5)
                    return HealthStatus(success=True, status="OK", message="Successfully connected (Simulated mode: placeholder API key)", latency=60.0)

                # Fetch models or hit validation endpoint
                url = f"{base_url}/v1/messages"
                payload = {
                    "model": config.configuration.get("model", "claude-3-5-sonnet-20240620"),
                    "messages": [{"role": "user", "content": "Ping"}],
                    "max_tokens": 1
                }
                req = urllib.request.Request(
                    url=url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    latency = (time.time() - start) * 1000
                    return HealthStatus(success=True, status="OK", message="Successfully connected to Anthropic.", latency=latency)
            except Exception as e:
                # If we get a validation or auth error, format it nicely
                latency = (time.time() - start) * 1000
                if isinstance(e, urllib.error.HTTPError):
                    try:
                        err_body = e.read().decode("utf-8")
                        err_json = json.loads(err_body)
                        msg = err_json["error"].get("message") or err_json["error"]
                        return HealthStatus(success=False, status="ERROR", message=f"Anthropic error ({e.code}): {msg}", latency=latency)
                    except Exception:
                        pass
                return HealthStatus(success=False, status="ERROR", message=f"Connection failed: {e}", latency=latency)

        raise ProviderError(f"Unsupported action: {action_id}")
        
    def stream_generate(self, request: 'InferenceRequest') -> Any:
        from backend.domain.events import GenerationStarted, TokenReceived, GenerationCompleted, GenerationFailed
        import time
        import json
        import urllib.request
        import urllib.error
        
        base_url = request.parameters.get("base_url", "https://api.anthropic.com")
        api_key = request.parameters.get("api_key", "")
        model_id = request.parameters.get("model", "claude-3-5-sonnet-20240620")

        yield GenerationStarted(session_id=request.session_id, model=model_id)

        # Fallback to mock simulation if placeholder key is used
        if not api_key or api_key == "mock" or "YOUR_" in api_key:
            text = f"This is a mock response from Anthropic Claude running via endpoint {base_url} for the prompt: '{request.user_prompt}'\n"
            words = text.split(" ")
            for word in words:
                time.sleep(0.04)
                yield TokenReceived(text=word + " ")
            yield GenerationCompleted(finish_reason="stop", usage={"prompt": 12, "completion": len(words)}, latency=len(words) * 0.04)
            return

        # Real Anthropic SSE Streaming Call
        url = f"{base_url}/v1/messages"
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": request.user_prompt}],
            "max_tokens": int(request.parameters.get("max_tokens", 2048)),
            "temperature": request.parameters.get("temperature", 0.7),
            "stream": True
        }
        
        req = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
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
                        try:
                            obj = json.loads(data_str)
                            if obj.get("type") == "content_block_delta":
                                text = obj["delta"]["text"]
                                if text:
                                    yield TokenReceived(text=text)
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


class GeminiProvider(AIProvider):
    @classmethod
    def get_metadata(cls) -> ProviderMetadata:
        return ProviderMetadata(
            id="gemini",
            display_name="Google Gemini",
            category=ProviderCategory.NATIVE,
            description="Official integration with Google Gemini LLMs.",
            icon="gemini.svg"
        )
        
    def get_capabilities(self) -> ProviderCapability:
        return ProviderCapability(
            supports_streaming=True,
            supports_json_mode=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_system_prompts=True,
            max_context_length=1000000,
            max_output_tokens=8192
        )
        
    def get_config_schema(self) -> ConfigurationSchema:
        return ConfigurationSchema(fields=[
            SchemaField(id="base_url", label="Base URL", type=FieldType.TEXT, default="https://generativelanguage.googleapis.com"),
            SchemaField(id="api_key", label="API Key", type=FieldType.PASSWORD),
            SchemaField(
                id="model",
                label="Model ID",
                type=FieldType.SELECT,
                default="gemini-3.5-flash",
                options=[
                    "gemini-3.5-flash",
                    "gemini-3.1-pro",
                    "gemini-3-flash",
                    "gemini-3.1-flash-lite"
                ]
            ),
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

    def get_supported_actions(self) -> List['ProviderAction']:
        from backend.domain.models import ProviderAction
        return [
            ProviderAction(id="health_check", display_name="Health Check", description="Verify API connectivity", icon="activity.svg")
        ]
        
    def execute_action(self, action_id: str, config: 'ProviderConfiguration') -> Any:
        from backend.domain.models import HealthStatus, ProviderError
        import json
        import urllib.request
        import urllib.error
        import time

        base_url = config.configuration.get("base_url", "https://generativelanguage.googleapis.com")
        api_key = config.configuration.get("api_key", "")
        model_id = config.configuration.get("model", "gemini-1.5-pro")

        if action_id == "health_check":
            start = time.time()
            try:
                if not api_key or api_key == "mock" or "YOUR_" in api_key:
                    time.sleep(0.5)
                    return HealthStatus(success=True, status="OK", message="Successfully connected (Simulated mode: placeholder API key)", latency=50.0)

                # Perform a simple content generation ping with 1 token output
                url = f"{base_url}/v1beta/models/{model_id}:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": "Ping"}]}],
                    "generationConfig": {"maxOutputTokens": 1}
                }
                req = urllib.request.Request(
                    url=url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    latency = (time.time() - start) * 1000
                    return HealthStatus(success=True, status="OK", message="Successfully connected to Gemini API.", latency=latency)
            except Exception as e:
                latency = (time.time() - start) * 1000
                if isinstance(e, urllib.error.HTTPError):
                    try:
                        err_body = e.read().decode("utf-8")
                        err_json = json.loads(err_body)
                        msg = err_json["error"].get("message") or err_json["error"]
                        return HealthStatus(success=False, status="ERROR", message=f"Gemini error ({e.code}): {msg}", latency=latency)
                    except Exception:
                        pass
                return HealthStatus(success=False, status="ERROR", message=f"Connection failed: {e}", latency=latency)

        raise ProviderError(f"Unsupported action: {action_id}")
        
    def stream_generate(self, request: 'InferenceRequest') -> Any:
        from backend.domain.events import GenerationStarted, TokenReceived, GenerationCompleted, GenerationFailed
        import time
        import json
        import urllib.request
        import urllib.error
        
        base_url = request.parameters.get("base_url", "https://generativelanguage.googleapis.com")
        api_key = request.parameters.get("api_key", "")
        model_id = request.parameters.get("model", "gemini-1.5-pro")

        yield GenerationStarted(session_id=request.session_id, model=model_id)

        # Fallback to mock simulation if placeholder key is used
        if not api_key or api_key == "mock" or "YOUR_" in api_key:
            text = f"This is a mock response from Google Gemini running via endpoint {base_url} for the prompt: '{request.user_prompt}'\n"
            words = text.split(" ")
            for word in words:
                time.sleep(0.04)
                yield TokenReceived(text=word + " ")
            yield GenerationCompleted(finish_reason="stop", usage={"prompt": 8, "completion": len(words)}, latency=len(words) * 0.04)
            return

        # Real Google Gemini Streaming Call
        url = f"{base_url}/v1beta/models/{model_id}:streamGenerateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": request.user_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": request.parameters.get("temperature", 0.7),
                "maxOutputTokens": int(request.parameters.get("max_tokens", 2048))
            }
        }
        
        req = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            response = urllib.request.urlopen(req, timeout=30)
            buffer = ""
            for chunk in response:
                buffer += chunk.decode("utf-8")
                while True:
                    start = buffer.find("{")
                    if start == -1:
                        break
                    
                    # Track matching brackets
                    brace_count = 0
                    end = -1
                    for i in range(start, len(buffer)):
                        if buffer[i] == "{":
                            brace_count += 1
                        elif buffer[i] == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                end = i
                                break
                    if end != -1:
                        json_str = buffer[start:end+1]
                        buffer = buffer[end+1:]
                        try:
                            obj = json.loads(json_str)
                            text = obj["candidates"][0]["content"]["parts"][0]["text"]
                            if text:
                                yield TokenReceived(text=text)
                        except Exception:
                            pass
                    else:
                        break
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


class MistralProvider(AIProvider):
    @classmethod
    def get_metadata(cls) -> ProviderMetadata:
        return ProviderMetadata(
            id="mistral",
            display_name="Mistral AI (Mistibui)",
            category=ProviderCategory.NATIVE,
            description="Official integration with Mistral AI / Mistibui models.",
            icon="mistral.svg"
        )
        
    def get_capabilities(self) -> ProviderCapability:
        return ProviderCapability(
            supports_streaming=True,
            supports_json_mode=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_system_prompts=True,
            max_context_length=128000,
            max_output_tokens=8192
        )
        
    def get_config_schema(self) -> ConfigurationSchema:
        return ConfigurationSchema(fields=[
            SchemaField(id="base_url", label="Base URL", type=FieldType.TEXT, default="https://api.mistral.ai/v1"),
            SchemaField(id="api_key", label="API Key", type=FieldType.PASSWORD),
            SchemaField(
                id="model",
                label="Model ID",
                type=FieldType.SELECT,
                default="mistral-large-latest",
                options=[
                    "mistral-large-latest",
                    "mistral-large-3",
                    "mistral-small-latest",
                    "mistral-small-4",
                    "ministral-8b-latest",
                    "ministral-3b-latest",
                    "codestral-latest"
                ]
            ),
        ])
        
    def get_runtime_schema(self) -> RuntimeParameterSchema:
        return RuntimeParameterSchema(
            supports_temperature=True,
            supports_top_p=True,
            supports_max_tokens=True,
            supports_frequency_penalty=False,
            supports_presence_penalty=False,
            supports_repeat_penalty=False
        )

    def get_supported_actions(self) -> List['ProviderAction']:
        from backend.domain.models import ProviderAction
        return [
            ProviderAction(id="health_check", display_name="Health Check", description="Verify API connectivity", icon="activity.svg")
        ]
        
    def execute_action(self, action_id: str, config: 'ProviderConfiguration') -> Any:
        from backend.domain.models import HealthStatus, ProviderError
        import json
        import urllib.request
        import urllib.error
        import time

        base_url = config.configuration.get("base_url", "https://api.mistral.ai/v1")
        api_key = config.configuration.get("api_key", "")
        model_id = config.configuration.get("model", "mistral-large-latest")

        if action_id == "health_check":
            start = time.time()
            try:
                if not api_key or api_key == "mock" or "YOUR_" in api_key:
                    time.sleep(0.5)
                    return HealthStatus(success=True, status="OK", message="Successfully connected (Simulated mode: placeholder API key)", latency=65.0)

                # Perform a simple content generation ping with 1 token output
                url = f"{base_url}/chat/completions"
                payload = {
                    "model": model_id,
                    "messages": [{"role": "user", "content": "Ping"}],
                    "max_tokens": 1
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
                with urllib.request.urlopen(req, timeout=5) as response:
                    latency = (time.time() - start) * 1000
                    return HealthStatus(success=True, status="OK", message="Successfully connected to Mistral AI API.", latency=latency)
            except Exception as e:
                latency = (time.time() - start) * 1000
                if isinstance(e, urllib.error.HTTPError):
                    try:
                        err_body = e.read().decode("utf-8")
                        err_json = json.loads(err_body)
                        msg = err_json["error"].get("message") or err_json["error"]
                        return HealthStatus(success=False, status="ERROR", message=f"Mistral error ({e.code}): {msg}", latency=latency)
                    except Exception:
                        pass
                return HealthStatus(success=False, status="ERROR", message=f"Connection failed: {e}", latency=latency)

        raise ProviderError(f"Unsupported action: {action_id}")
        
    def stream_generate(self, request: 'InferenceRequest') -> Any:
        from backend.domain.events import GenerationStarted, TokenReceived, GenerationCompleted, GenerationFailed
        import time
        import json
        import urllib.request
        import urllib.error
        
        base_url = request.parameters.get("base_url", "https://api.mistral.ai/v1")
        api_key = request.parameters.get("api_key", "")
        model_id = request.parameters.get("model", "mistral-large-latest")

        yield GenerationStarted(session_id=request.session_id, model=model_id)

        # Fallback to mock simulation if placeholder key is used
        if not api_key or api_key == "mock" or "YOUR_" in api_key:
            text = f"This is a mock response from Mistral AI running via endpoint {base_url} for the prompt: '{request.user_prompt}'\n"
            words = text.split(" ")
            for word in words:
                time.sleep(0.04)
                yield TokenReceived(text=word + " ")
            yield GenerationCompleted(finish_reason="stop", usage={"prompt": 8, "completion": len(words)}, latency=len(words) * 0.04)
            return

        # Real Mistral SSE Streaming Call
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
