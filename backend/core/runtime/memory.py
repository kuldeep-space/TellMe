import os
from abc import ABC, abstractmethod
from typing import Tuple
from backend.core.runtime.models import MemoryPolicy
from backend.domain.models import ModelDescriptor

class BaseMemoryEstimator(ABC):
    """
    Engine-agnostic base memory estimator.
    """
    @abstractmethod
    def estimate_requirements(self, descriptor: ModelDescriptor, requested_ctx: int) -> Tuple[float, float, float]:
        """
        Estimate memory usage for a model.
        Returns:
            Tuple[float, float, float]: (Total memory MB, KV cache memory MB, Overhead MB)
        """
        pass

class LlamaCppMemoryEstimator(BaseMemoryEstimator):
    """Memory estimator specific to llama.cpp architectures."""
    def estimate_requirements(self, descriptor: ModelDescriptor, requested_ctx: int) -> Tuple[float, float, float]:
        # 1. Model weights
        model_size_bytes = descriptor.size_bytes

        # 2. KV Cache
        arch = descriptor.metadata.get('general.architecture', 'llama')
        n_layers = int(descriptor.metadata.get(f'{arch}.block_count', 0))
        n_embd = int(descriptor.metadata.get(f'{arch}.embedding_length', 0))
        n_head = int(descriptor.metadata.get(f'{arch}.attention.head_count', 0))
        n_head_kv = int(descriptor.metadata.get(f'{arch}.attention.head_count_kv', n_head))
        
        kv_cache_bytes = 0
        if n_layers > 0 and n_embd > 0 and n_head > 0:
            # size = 2 (K,V) * 2 (f16) * layers * ctx * (embd/head) * head_kv
            head_dim = n_embd // n_head
            kv_cache_bytes = 4 * n_layers * requested_ctx * head_dim * n_head_kv
        
        # 3. Overhead (Compute buffers, Python, OS)
        # llama.cpp uses a compute buffer that scales with batch size and context. 
        # Safely overestimate overhead as 500 MB base + 10% of model size.
        overhead_bytes = (500 * 1024 * 1024) + (model_size_bytes * 0.10)

        total_bytes = model_size_bytes + kv_cache_bytes + overhead_bytes
        
        return (
            total_bytes / (1024 * 1024),
            kv_cache_bytes / (1024 * 1024),
            overhead_bytes / (1024 * 1024)
        )
