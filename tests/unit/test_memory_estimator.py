import unittest
from backend.core.runtime.memory import LlamaCppMemoryEstimator
from backend.domain.models import ModelDescriptor, ModelFormat

class TestMemoryEstimator(unittest.TestCase):
    def test_llama_cpp_estimation(self):
        estimator = LlamaCppMemoryEstimator()
        
        # Fake a 14B Qwen-like model
        descriptor = ModelDescriptor(
            id="qwen",
            display_name="Qwen",
            path="qwen.gguf",
            size_bytes=10 * 1024 * 1024 * 1024, # 10GB
            format=ModelFormat.GGUF,
            architecture="qwen2",
            metadata={
                "general.architecture": "qwen2",
                "qwen2.block_count": 40,
                "qwen2.embedding_length": 5120,
                "qwen2.attention.head_count": 40,
                "qwen2.attention.head_count_kv": 8
            }
        )
        
        # 1. Test standard context
        total, kv, overhead = estimator.estimate_requirements(descriptor, 4096)
        
        # head_dim = 5120 / 40 = 128
        # kv_bytes = 4 * 40 * 4096 * 128 * 8 = 671,088,640 bytes = 640 MB
        self.assertAlmostEqual(kv, 640.0, places=1)
        
        # Overhead: 500 MB base + 10% of 10GB = 1524 MB
        self.assertAlmostEqual(overhead, 1524.0, places=1)
        
        # 2. Test large context
        total2, kv2, overhead2 = estimator.estimate_requirements(descriptor, 32768)
        self.assertAlmostEqual(kv2, 5120.0, places=1) # 8x context -> 8x KV

if __name__ == '__main__':
    unittest.main()
