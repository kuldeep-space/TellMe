import logging
from typing import Optional, Any, Dict
from backend.domain.models import ModelDescriptor, ModelState, RuntimeStatus
from backend.core.runtime.manager import RuntimeManager
from backend.core.runtime.models import SessionState, RuntimeDiagnostics, InferenceRequest

logger = logging.getLogger(__name__)

class ModelRuntime:
    """
    Adapter/Proxy over RuntimeManager to maintain compatibility with existing code.
    Manages a single active session through the modern runtime architecture.
    """
    _instance: Optional["ModelRuntime"] = None

    def __init__(self):
        self._manager = RuntimeManager()
        self._active_model_id: Optional[str] = None
        self._states: Dict[str, ModelState] = {}

    @classmethod
    def get_instance(cls) -> "ModelRuntime":
        if cls._instance is None:
            cls._instance = ModelRuntime()
        return cls._instance

    @property
    def active_model_id(self) -> Optional[str]:
        return self._active_model_id

    def load_model(self, descriptor: ModelDescriptor, user_config: Optional[Dict[str, Any]] = None):
        """Loads a model via the RuntimeManager."""
        try:
            self._update_state(descriptor.id, status=RuntimeStatus.LOADING)
            
            # Use RuntimeManager to orchestrate the entire process
            session = self._manager.load_model(descriptor, engine_id="llama.cpp", user_config=user_config)
            
            self._active_model_id = descriptor.id
            self._update_state(descriptor.id, status=RuntimeStatus.LOADED)
            logger.info(f"ModelRuntime: Successfully loaded '{descriptor.id}'")
            
        except Exception as e:
            self._update_state(descriptor.id, status=RuntimeStatus.ERROR)
            raise

    def get_generator(self, request: Any) -> Any:
        """Returns the generation iterator for the active session."""
        if not self._active_model_id:
            raise RuntimeError("No model is currently loaded.")
            
        session = self._manager.find_session(self._active_model_id)
        if not session:
            raise RuntimeError("No active session found for the loaded model.")
        
        # Convert legacy InferenceRequest to core runtime InferenceRequest if needed
        # Or just pass it through if compatible
        from backend.core.runtime.models import InferenceRequest as CoreInferenceRequest
        
        prompt = ""
        max_tokens = 512
        temperature = 0.7
        top_p = 0.95
        stop = []
        stream = True
        
        if hasattr(request, 'messages') and isinstance(request.messages, list):
            # Very basic stringification for testing, actual conversion depends on model
            prompt = "\n".join([f"{m.role}: {m.content}" for m in request.messages]) + "\nassistant:"
            if hasattr(request, 'parameters'):
                max_tokens = request.parameters.get("max_tokens", 512)
                temperature = request.parameters.get("temperature", 0.7)
                top_p = request.parameters.get("top_p", 0.95)
                stop = request.parameters.get("stop", [])
        
        core_req = CoreInferenceRequest(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop_sequences=stop,
            stream=stream
        )
        
        return session.generate(core_req)

    def cancel_generation(self):
        """Cancels generation on the active session."""
        if self._active_model_id:
            session = self._manager.find_session(self._active_model_id)
            if session:
                session.cancel()

    def unload_model(self, model_id: str):
        """Unloads the model via RuntimeManager."""
        self._manager.unload_model(model_id)
        if self._active_model_id == model_id:
            self._active_model_id = None
        self._update_state(model_id, status=RuntimeStatus.UNLOADED)
        logger.info(f"ModelRuntime: Unloaded '{model_id}'")

    def shutdown(self):
        """Global cleanup."""
        self._manager.shutdown()
        self._active_model_id = None
        self._states.clear()

    def get_diagnostics(self) -> Optional[RuntimeDiagnostics]:
        if self._active_model_id:
            session = self._manager.find_session(self._active_model_id)
            if session:
                return session.diagnostics
        return None

    def _update_state(self, model_id: str, status: RuntimeStatus):
        if model_id not in self._states:
            self._states[model_id] = ModelState(
                model_id=model_id,
                status=RuntimeStatus.UNLOADED,
                last_used=None,
                memory_usage_bytes=0
            )
        self._states[model_id].status = status
