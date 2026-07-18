from typing import Dict, Any, Optional
from backend.domain.models import ModelDescriptor
from backend.core.runtime.models import MemoryPolicy
from backend.core.runtime.interfaces import RuntimeEngine, RuntimeSession
from backend.core.runtime.planner import RuntimePlanner
from backend.core.runtime.validator import RuntimeValidator
from backend.core.runtime.monitor import ResourceMonitor

class RuntimeEngineFactory:
    """Instantiates and configures RuntimeEngine implementations."""
    
    @staticmethod
    def create_engine(engine_id: str) -> RuntimeEngine:
        if engine_id == "llama.cpp":
            from backend.providers.engines.llama_cpp_engine import LlamaCppEngine
            return LlamaCppEngine()
        else:
            raise ValueError(f"Unknown engine: {engine_id}")

class RuntimeManager:
    """
    Central orchestration layer for the AI runtime.
    Manages engine discovery, selection, and session creation.
    """
    
    def __init__(self):
        self._engines: Dict[str, RuntimeEngine] = {}
        self._active_sessions: Dict[str, RuntimeSession] = {}
        
    def initialize_engine(self, engine_id: str):
        if engine_id not in self._engines:
            engine = RuntimeEngineFactory.create_engine(engine_id)
            engine.initialize()
            self._engines[engine_id] = engine

    def load_model(self, descriptor: ModelDescriptor, engine_id: str = "llama.cpp", user_config: Optional[Dict[str, Any]] = None) -> RuntimeSession:
        if descriptor.id in self._active_sessions:
            return self._active_sessions[descriptor.id]

        if user_config is None:
            user_config = {}

        self.initialize_engine(engine_id)
        engine = self._engines[engine_id]
        
        snapshot = ResourceMonitor.get_snapshot()
        capabilities = engine.get_capabilities()
        
        # 1. Validate
        RuntimeValidator.validate(descriptor, capabilities, snapshot.available_ram_mb)
        
        # 2. Plan
        from backend.config.settings import get_settings
        settings = get_settings()
        allow_unsafe = getattr(settings, "allow_unsafe_loading", False)
        
        estimator = engine.create_memory_estimator()
        policy = MemoryPolicy(allow_unsafe_loading=allow_unsafe)

        plan = RuntimePlanner.plan(
            engine_id=engine_id,
            backend_version="1.0.0", # TODO: Get from engine
            descriptor=descriptor,
            capabilities=capabilities,
            estimator=estimator,
            policy=policy,
            available_ram_mb=snapshot.available_ram_mb,
            user_config=user_config
        )
        
        # 3. Load
        session = engine.load_model(plan)
        
        # Store active session (simple single model implementation for now)
        self._active_sessions[descriptor.id] = session
        
        return session
        
    def unload_model(self, model_id: str):
        if model_id in self._active_sessions:
            session = self._active_sessions[model_id]
            session.shutdown()
            del self._active_sessions[model_id]

    def get_active_sessions(self) -> Dict[str, RuntimeSession]:
        """Returns a copy of all active sessions."""
        return dict(self._active_sessions)

    def active_session_count(self) -> int:
        """Returns the number of active sessions."""
        return len(self._active_sessions)

    def find_session(self, model_id: str) -> Optional[RuntimeSession]:
        """Finds an active session by model_id, returning None if not found."""
        return self._active_sessions.get(model_id)

    def shutdown(self):
        """Global cleanup."""
        for session in list(self._active_sessions.values()):
            session.shutdown()
        self._active_sessions.clear()
        
        for engine in self._engines.values():
            engine.shutdown()
        self._engines.clear()
