"""
Core Service: AI Engine.

Central orchestration layer. Routes InferenceRequests to the correct
ModelRuntime session and streams back structured events.

The AIEngine is focused purely on orchestration. It does NOT:
- Hold any model objects.
- Manage VRAM or memory.
- Know about specific inference engine implementations.

All resource management is delegated to ModelRuntime.
"""
import time
import logging
from typing import Generator, Any

from backend.domain.models import (
    InferenceRequest, ProviderError, ConfigurationError,
    ModelDescriptor
)
from backend.domain.events import StreamEvent, GenerationStarted, GenerationFailed, TokenReceived, GenerationCompleted
from backend.core.model_registry import ModelRegistry
from backend.core.model_runtime import ModelRuntime
from backend.core.engine_resolver import EngineResolver

logger = logging.getLogger(__name__)


class AIEngine:
    """
    Central orchestration layer.
    Sits between the business logic (PlaygroundService, InterviewEngine)
    and the ModelRuntime.

    Expects `request.parameters` to contain either:
    - `model_id`: A LocalModel ID from the ModelRegistry (local inference).
    - `provider_id`: A legacy cloud provider ID (API-based inference).
    """

    @classmethod
    def stream_generate(cls, request: InferenceRequest) -> Generator[StreamEvent, None, None]:
        start_time = time.time()
        model_id = request.parameters.get("model_id")
        provider_id = request.parameters.get("provider_id")

        try:
            if model_id:
                yield from cls._stream_local(request, model_id, start_time)
            elif provider_id:
                yield from cls._stream_provider(request, provider_id, start_time)
            else:
                raise ConfigurationError(
                    "No 'model_id' or 'provider_id' specified in request parameters."
                )
        except ProviderError:
            raise
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"AIEngine: Request failed in {duration:.2f}s — {e}")
            normalized = cls._normalize_error(e)
            yield GenerationFailed(
                error_message=str(normalized),
                error_type=normalized.__class__.__name__
            )
            raise normalized

    # ------------------------------------------------------------------
    # Local inference path (ModelRuntime -> llama.cpp / etc.)
    # ------------------------------------------------------------------

    @classmethod
    def _stream_local(cls, request: InferenceRequest, model_id: str, start_time: float):
        registry = ModelRegistry.get_instance()
        descriptor = registry.get(model_id)
        if not descriptor:
            raise ConfigurationError(f"Model '{model_id}' not found in registry.")

        runtime = ModelRuntime.get_instance()
        runtime_config = request.parameters  # n_gpu_layers, context_length, etc.

        logger.info(f"AIEngine: Local inference — model='{descriptor.display_name}'")

        # Load the model if not loaded (using the new architecture)
        if runtime.active_model_id != descriptor.id:
            runtime.load_model(descriptor, runtime_config)

        # Emit diagnostics
        diags = runtime.get_diagnostics()
        if diags:
            from backend.core.runtime.events import DiagnosticsUpdated
            yield DiagnosticsUpdated(
                model_id=descriptor.id,
                diagnostics=diags
            )

        yield GenerationStarted(
            session_id=request.session_id,
            model=descriptor.display_name
        )

        stream = runtime.get_generator(request)

        total_tokens = 0
        for response in stream:
            text = response.text
            if text:
                total_tokens += 1
                yield TokenReceived(text=text)

        duration = time.time() - start_time
        yield GenerationCompleted(
            finish_reason="stop",
            usage={"completion": total_tokens},
            latency=duration,
        )
        logger.info(f"AIEngine: Local stream complete in {duration:.2f}s "
                    f"({total_tokens} tokens).")

    # ------------------------------------------------------------------
    # Cloud/API provider path (legacy — forwards to ProviderRegistry)
    # ------------------------------------------------------------------

    @classmethod
    def _stream_provider(cls, request: InferenceRequest, provider_id: str, start_time: float):
        from backend.core.provider_registry import ProviderRegistry

        logger.info(f"AIEngine: API inference — provider='{provider_id}'")
        provider = ProviderRegistry.get_provider(provider_id)

        if not hasattr(provider, "stream_generate"):
            raise ProviderError(f"Provider '{provider_id}' does not support stream_generate.")

        yield from provider.stream_generate(request)

        duration = time.time() - start_time
        logger.info(f"AIEngine: Provider stream complete in {duration:.2f}s.")

    # ------------------------------------------------------------------
    # Error normalization
    # ------------------------------------------------------------------

    @classmethod
    def _normalize_error(cls, e: Exception) -> ProviderError:
        if isinstance(e, ProviderError):
            return e
        err_str = str(e).lower()
        if "connection refused" in err_str or "timeout" in err_str:
            from backend.domain.models import ConnectionError
            return ConnectionError(f"Failed to connect to provider backend: {e}")
        if "unauthorized" in err_str or "api key" in err_str or "401" in err_str:
            from backend.domain.models import AuthenticationError
            return AuthenticationError(f"Authentication failed: {e}")
        return ProviderError(f"An unexpected provider error occurred: {e}")
