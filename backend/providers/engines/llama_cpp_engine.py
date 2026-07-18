import gc
import time
import logging
import os
import sys
from typing import Iterator, Optional

# On Windows, add the llama_cpp/lib directory and project local dependencies to the DLL search path
# so that dynamic backend DLLs (like ggml-cpu-*.dll) can be resolved.
if sys.platform == "win32":
    try:
        # 1. Project local dependencies directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        local_bin_dir = os.path.join(project_root, "dependencies", "llama_binaries")
        if os.path.isdir(local_bin_dir):
            os.add_dll_directory(local_bin_dir)
            logging.info(f"LlamaCppEngine: Added local DLL directory {local_bin_dir} to search path.")

        # 2. Installed llama_cpp package directory
        import llama_cpp
        lib_dir = os.path.join(os.path.dirname(llama_cpp.__file__), "lib")
        if os.path.isdir(lib_dir):
            os.add_dll_directory(lib_dir)
            logging.info(f"LlamaCppEngine: Added DLL directory {lib_dir} to search path.")
    except Exception as e:
        logging.warning(f"LlamaCppEngine: Failed to configure DLL search paths: {e}")


from backend.core.runtime.interfaces import RuntimeEngine, RuntimeSession

from backend.core.runtime.models import (
    RuntimePlan, EngineCapabilities, SessionState, RuntimeDiagnostics,
    InferenceRequest, InferenceResponse
)
from backend.core.runtime.events import EventBus, ModelLoaded, ModelUnloaded, GenerationStarted, GenerationFinished, GenerationCancelled, RuntimeErrorEvent
from backend.core.runtime.memory import BaseMemoryEstimator, LlamaCppMemoryEstimator
from backend.core.runtime.monitor import ResourceMonitor

logger = logging.getLogger(__name__)

class LlamaCppSession(RuntimeSession):
    def __init__(self, plan: RuntimePlan):
        self._plan = plan
        self._state = SessionState.CREATED
        self._diagnostics = None
        self._llama = None
        
    @property
    def plan(self) -> RuntimePlan:
        return self._plan

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def diagnostics(self) -> Optional[RuntimeDiagnostics]:
        return self._diagnostics

    def load(self):
        from llama_cpp import Llama

        self._state = SessionState.INITIALIZING
        start_time = time.time()
        
        try:
            self._state = SessionState.LOADING
            ram_before = ResourceMonitor.get_snapshot().process_ram_mb
            
            # Instantiate llama.cpp
            self._llama = Llama(
                model_path=self._plan.model_path,
                n_ctx=self._plan.context_length,
                n_batch=self._plan.batch_size,
                n_ubatch=self._plan.ubatch_size,
                n_threads=self._plan.thread_count,
                n_threads_batch=self._plan.thread_batch_count,
                n_gpu_layers=self._plan.gpu_layers,
                use_mmap=self._plan.use_mmap,
                use_mlock=self._plan.use_mlock,
                flash_attn=self._plan.use_flash_attention,
                verbose=False
            )
            
            load_time = time.time() - start_time
            ram_after = ResourceMonitor.get_snapshot().process_ram_mb
            actual_memory_mb = ram_after - ram_before
            
            # Construct immutable diagnostics
            import llama_cpp
            self._diagnostics = RuntimeDiagnostics(
                engine=self._plan.engine_id,
                backend_version=llama_cpp.__version__,
                runtime_version="1.0.0",
                model_name=self._plan.model_id,
                architecture=self._plan.architecture,
                quantization="unknown", # Could extract from metadata
                model_size_mb=0, # Could pass from plan
                requested_context=self._plan.context_length, # This assumes plan has actual context, which we do
                actual_context=self._plan.context_length,
                batch_size=self._plan.batch_size,
                thread_configuration=f"{self._plan.thread_count}/{self._plan.thread_batch_count}",
                gpu_layers=self._plan.gpu_layers,
                estimated_memory_mb=self._plan.estimated_memory_mb,
                actual_memory_mb=actual_memory_mb,
                available_ram_before_mb=self._plan.available_memory_mb,
                available_ram_after_mb=ResourceMonitor.get_snapshot().available_ram_mb,
                kv_cache_estimate_mb=0, # Omitted for brevity in extraction
                compute_buffer_estimate_mb=0,
                load_time_sec=load_time,
                initialization_time_sec=0,
                context_reduced=self._plan.context_reduced,
                unsafe_configuration=False,
                policy_overrides=self._plan.policy_overrides
            )
            
            self._state = SessionState.READY
            
            EventBus.publish(ModelLoaded(
                model_id=self._plan.model_id,
                engine_id=self._plan.engine_id,
                context_length=self._plan.context_length
            ))
            from backend.core.runtime.events import DiagnosticsUpdated
            EventBus.publish(DiagnosticsUpdated(
                model_id=self._plan.model_id,
                diagnostics=self._diagnostics
            ))
            
        except Exception as e:
            self._state = SessionState.FAILED
            logger.error(f"Failed to load Llama model: {e}", exc_info=True)
            self._cleanup_native()
            EventBus.publish(RuntimeErrorEvent(error=str(e), source="LlamaCppSession"))
            raise RuntimeError(f"Failed to create llama_context: {e}") from e

    def generate(self, request: InferenceRequest) -> Iterator[InferenceResponse]:
        if self._state != SessionState.READY:
            raise RuntimeError(f"Cannot generate from state: {self._state}")
            
        self._state = SessionState.GENERATING
        start_time = time.time()
        tokens = 0
        
        EventBus.publish(GenerationStarted(model_id=self._plan.model_id, prompt_length=len(request.prompt)))
        
        try:
            assert self._llama is not None
            generator = self._llama.create_completion(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stop=request.stop_sequences,
                stream=request.stream
            )
            
            for chunk in generator:
                if self._state == SessionState.CANCELLING:
                    EventBus.publish(GenerationCancelled(model_id=self._plan.model_id))
                    break
                    
                if request.stream:
                    text = chunk['choices'][0]['text']
                    finish_reason = chunk['choices'][0]['finish_reason']
                    usage = {} # Not always available in stream chunks
                else:
                    text = chunk['choices'][0]['text']
                    finish_reason = chunk['choices'][0]['finish_reason']
                    usage = chunk.get('usage', {})
                    
                tokens += 1
                yield InferenceResponse(text=text, finish_reason=finish_reason, usage=usage)
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            EventBus.publish(RuntimeErrorEvent(error=str(e), source="LlamaCppSession:generate"))
            raise
        finally:
            if self._state != SessionState.CANCELLING:
                self._state = SessionState.READY
                total_time = time.time() - start_time
                EventBus.publish(GenerationFinished(
                    model_id=self._plan.model_id,
                    tokens_generated=tokens,
                    total_time_sec=total_time
                ))

    def cancel(self):
        if self._state == SessionState.GENERATING:
            self._state = SessionState.CANCELLING

    def shutdown(self):
        self._state = SessionState.UNLOADING
        self._cleanup_native()
        self._state = SessionState.CLOSED
        EventBus.publish(ModelUnloaded(model_id=self._plan.model_id))

    def _cleanup_native(self):
        if self._llama:
            self._llama.close()
            del self._llama
            self._llama = None
        gc.collect()

class LlamaCppEngine(RuntimeEngine):
    def initialize(self):
        pass

    def get_capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supports_gpu_layers=True,
            supports_flash_attention=True,
            supports_embeddings=True,
            supports_streaming=True,
            supports_mmap=True,
            supports_mlock=True,
            supports_batching=True,
            supports_vision=False,
            supports_tool_calling=False
        )

    def create_memory_estimator(self) -> BaseMemoryEstimator:
        return LlamaCppMemoryEstimator()

    def load_model(self, plan: RuntimePlan) -> RuntimeSession:
        session = LlamaCppSession(plan)
        session.load()
        return session

    def shutdown(self):
        pass
