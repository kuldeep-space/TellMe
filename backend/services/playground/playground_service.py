import logging
from typing import Dict, Any, Callable
from backend.domain.models import InferenceRequest, InferenceMessage
from backend.domain.session import AISession
from backend.core.tasks import TaskManager
from backend.core.engine import AIEngine
from backend.domain.events import StreamEvent, GenerationFailed

logger = logging.getLogger(__name__)

class PlaygroundService:
    """
    Dedicated service for the Playground UI.
    Uses TaskManager to boot an AISession, dispatches it to the AIEngine, 
    and routes structured events back to the UI.
    """
    
    def __init__(self):
        self.task_manager = TaskManager.get_instance()
        
    def execute_action(self, provider_id: str, action_id: str, on_result: Callable, on_error: Callable) -> str:
        """
        Executes a dynamic provider action in the background.
        """
        def _action_worker(worker=None):
            from backend.core.provider_registry import ProviderRegistry
            from backend.domain.provider import ProviderConfiguration, ProviderType, ProviderCategory
            import json, os
            
            # Reconstruct the config (in a real app, this might use a DB)
            config_path = os.path.join("D:\\TellMe\\runtime", "model_config.json")
            config_data = {}
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    data = json.load(f)
                    if data.get("provider_id") == provider_id:
                        config_data = data.get("configuration", {})
                        
            provider = ProviderRegistry.get_provider(provider_id)
            meta = provider.get_metadata()
            backend_type = ProviderType.LOCAL if meta.category == ProviderCategory.LOCAL else ProviderType.API
            
            cfg = ProviderConfiguration(
                provider_id=provider_id,
                backend_type=backend_type,
                display_name=meta.display_name,
                configuration=config_data
            )
            return provider.execute_action(action_id, cfg)
            
        # Hook up signals manually
        task_id = self.task_manager.submit(_action_worker, worker=None)
        worker = self.task_manager.get_worker(task_id)
        if worker:
            worker.signals.result.connect(lambda t_id, res: on_result(res))
            worker.signals.error.connect(lambda t_id, err: on_error(err))
            
        return task_id
        
    def stream_generation(self, session: AISession, system_prompt: str, user_prompt: str, params: Dict[str, Any], on_event: Callable) -> str:
        """
        Starts an asynchronous generation using the AIEngine.
        Automatically uses a local model from the ModelRegistry if one is selected,
        otherwise falls back to the legacy API provider path.
        """
        def _generation_worker(worker=None):
            import json, os
            final_params = dict(params)

            # ── Resolve model_id from ModelRegistry (local models) ───────────
            config_path = os.path.join("D:\\TellMe\\runtime", "model_config.json")
            selected_model_id = None
            cfg = {}
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as f:
                        cfg = json.load(f)
                    selected_model_id = cfg.get("selected_model_id")
                except Exception:
                    pass

            # ── Load global runtime config ────────────────────────────────────
            runtime_path = os.path.join("D:\\TellMe\\runtime", "runtime_config.json")
            if os.path.exists(runtime_path):
                try:
                    with open(runtime_path, "r") as f:
                        runtime_cfg = json.load(f)
                    # Only apply runtime config values not already in params
                    for k, v in runtime_cfg.items():
                        final_params.setdefault(k, v)
                except Exception:
                    pass

            if selected_model_id:
                # Local model path
                final_params["model_id"] = selected_model_id
            else:
                # API provider path — use saved provider_id and its config
                saved_provider_id = cfg.get("provider_id")
                saved_config = cfg.get("configuration", {})
                provider_id = saved_provider_id or session.provider_id
                final_params["provider_id"] = provider_id
                # Merge saved provider config (API key, base_url, model) into params
                for k, v in saved_config.items():
                    final_params.setdefault(k, v)

            request = InferenceRequest(
                session_id=session.session_id,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                messages=[InferenceMessage(role="user", content=user_prompt)],
                parameters=final_params
            )

            import time
            from backend.domain.events import TokenReceived
            
            generator = AIEngine.stream_generate(request)
            
            token_buffer = ""
            last_flush = time.time()
            flush_interval = 0.05  # Flush UI every 50ms to prevent GUI locking
            
            for event in generator:
                if worker and worker.is_cancelled:
                    logger.info("Playground generation cancelled.")
                    break
                
                if worker:
                    if isinstance(event, TokenReceived):
                        token_buffer += event.text
                        now = time.time()
                        if now - last_flush >= flush_interval:
                            worker.signals.stream_event.emit(worker.task_id, TokenReceived(text=token_buffer))
                            token_buffer = ""
                            last_flush = now
                    else:
                        if token_buffer:
                            worker.signals.stream_event.emit(worker.task_id, TokenReceived(text=token_buffer))
                            token_buffer = ""
                        worker.signals.stream_event.emit(worker.task_id, event)

            if worker and token_buffer:
                worker.signals.stream_event.emit(worker.task_id, TokenReceived(text=token_buffer))

        task_id = self.task_manager.submit(_generation_worker, worker=None)
        worker = self.task_manager.get_worker(task_id)
        if worker:
            worker.signals.stream_event.connect(lambda t_id, evt: on_event(evt))
            def _on_err(t_id, err):
                logger.error(f"Playground task error: {err}", exc_info=err)
                on_event(GenerationFailed(error_message=str(err), error_type=err.__class__.__name__))
            worker.signals.error.connect(_on_err)
        return task_id
        
    def cancel_task(self, task_id: str):
        self.task_manager.cancel(task_id)
