import multiprocessing
import logging
from typing import Dict, Any, Type
from backend.domain.models import ModelDescriptor
from backend.core.runtime.models import RuntimePlan, MemoryPolicy, EngineCapabilities
from backend.core.runtime.memory import BaseMemoryEstimator

logger = logging.getLogger(__name__)

class RuntimePlanner:
    """Orchestrates the decision-making process to generate an immutable RuntimePlan."""

    @staticmethod
    def plan(
        engine_id: str,
        backend_version: str,
        descriptor: ModelDescriptor,
        capabilities: EngineCapabilities,
        estimator: BaseMemoryEstimator,
        policy: MemoryPolicy,
        available_ram_mb: float,
        user_config: Dict[str, Any]
    ) -> RuntimePlan:
        
        # 1. Thread selection
        physical_cores = max(1, multiprocessing.cpu_count() // 2)
        logical_cores = multiprocessing.cpu_count()
        thread_count = user_config.get("n_threads", physical_cores)
        thread_batch_count = user_config.get("n_threads_batch", logical_cores)

        # 2. Context Length and Memory Safety
        requested_ctx = user_config.get("context_length", descriptor.capabilities.context_length)
        actual_ctx = requested_ctx
        context_reduced = False
        warnings = []

        total_est, kv_est, overhead_est = estimator.estimate_requirements(descriptor, requested_ctx)
        
        safe_ram_mb = available_ram_mb * (1.0 - policy.safety_margin_percent)
        
        if total_est > safe_ram_mb and not policy.allow_unsafe_loading:
            # We need to scale down the context length
            logger.warning(f"RuntimePlanner: Estimated memory ({total_est:.1f}MB) exceeds safe limit ({safe_ram_mb:.1f}MB). Attempting reduction.")
            # Binary search or simple ratio for safe context
            # Since KV cache scales linearly with ctx:
            non_kv_memory = total_est - kv_est
            allowable_kv = safe_ram_mb - non_kv_memory
            
            if allowable_kv <= 0:
                raise MemoryError(f"Model weights and overhead ({non_kv_memory:.1f}MB) exceed safe RAM limit ({safe_ram_mb:.1f}MB) even with 0 context.")
                
            # Scale ctx linearly
            ratio = allowable_kv / kv_est
            actual_ctx = max(512, int(requested_ctx * ratio))
            
            # Re-estimate to be safe
            total_est, _, _ = estimator.estimate_requirements(descriptor, actual_ctx)
            
            context_reduced = True
            warn_msg = f"Context reduced from {requested_ctx} to {actual_ctx} to fit within {safe_ram_mb:.1f}MB safe RAM limit."
            warnings.append(warn_msg)
            logger.warning(warn_msg)

        # 3. GPU Layers
        gpu_layers = user_config.get("n_gpu_layers", -1) if capabilities.supports_gpu_layers else 0

        # 4. Features
        use_mmap = user_config.get("use_mmap", True) if capabilities.supports_mmap else False
        use_mlock = user_config.get("use_mlock", False) if capabilities.supports_mlock else False
        use_flash_attention = user_config.get("flash_attn", True) if capabilities.supports_flash_attention else False

        return RuntimePlan(
            engine_id=engine_id,
            backend_version=backend_version,
            model_id=descriptor.id,
            model_path=descriptor.path,
            architecture=descriptor.metadata.get('general.architecture', 'unknown'),
            context_length=actual_ctx,
            batch_size=512,
            ubatch_size=512,
            thread_count=thread_count,
            thread_batch_count=thread_batch_count,
            gpu_layers=gpu_layers,
            estimated_memory_mb=total_est,
            available_memory_mb=available_ram_mb,
            safety_margin_mb=available_ram_mb * policy.safety_margin_percent,
            use_mmap=use_mmap,
            use_mlock=use_mlock,
            use_flash_attention=use_flash_attention,
            context_reduced=context_reduced,
            policy_overrides=warnings
        )
