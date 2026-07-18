import unittest
from backend.core.runtime.planner import RuntimePlanner
from backend.core.runtime.models import EngineCapabilities, MemoryPolicy
from backend.core.runtime.memory import BaseMemoryEstimator
from backend.domain.models import ModelDescriptor, ModelFormat

class MockEstimator(BaseMemoryEstimator):
    def estimate_requirements(self, descriptor, ctx):
        # Fake logic: 10GB base + 1GB per 1024 ctx
        return (10000 + (ctx / 1024) * 1000, (ctx / 1024) * 1000, 10000)

class TestRuntimePlanner(unittest.TestCase):
    def setUp(self):
        self.capabilities = EngineCapabilities(
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
        self.descriptor = ModelDescriptor(
            id="test", display_name="Test", path="test.gguf", 
            size_bytes=10000000000, format=ModelFormat.GGUF, architecture="test", metadata={}
        )

    def test_safe_context(self):
        estimator = MockEstimator()
        policy = MemoryPolicy(safety_margin_percent=0.1)
        
        # We have 16GB RAM. Safe RAM = 14.4GB (14400 MB)
        # 10GB base + ctx cost. Context cost can be up to 4.4GB
        # 4.4GB = 4400MB -> ctx = 4.4 * 1024 = 4505
        
        # Requesting 8192 context -> requires 10000 + 8000 = 18GB -> should reduce
        plan = RuntimePlanner.plan(
            engine_id="test_engine",
            backend_version="1.0",
            descriptor=self.descriptor,
            capabilities=self.capabilities,
            estimator=estimator,
            policy=policy,
            available_ram_mb=16000,
            user_config={"context_length": 8192}
        )
        
        self.assertTrue(plan.context_reduced)
        self.assertTrue(plan.context_length < 8192)
        # Should be ~4505
        self.assertTrue(4400 <= plan.context_length <= 4600)
        
    def test_unsafe_context_override(self):
        estimator = MockEstimator()
        policy = MemoryPolicy(safety_margin_percent=0.1, allow_unsafe_loading=True)
        
        plan = RuntimePlanner.plan(
            engine_id="test_engine",
            backend_version="1.0",
            descriptor=self.descriptor,
            capabilities=self.capabilities,
            estimator=estimator,
            policy=policy,
            available_ram_mb=16000,
            user_config={"context_length": 8192}
        )
        
        # Shouldn't reduce if unsafe loading is allowed
        self.assertFalse(plan.context_reduced)
        self.assertEqual(plan.context_length, 8192)

if __name__ == '__main__':
    unittest.main()
