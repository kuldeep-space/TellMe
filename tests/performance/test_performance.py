import os
import time
import unittest
import subprocess

from backend.core.runtime.manager import RuntimeManager
from backend.domain.models import ModelDescriptor, ModelFormat
from backend.core.runtime.models import InferenceRequest
from backend.core.runtime.validator import RuntimeValidator
from backend.core.runtime.monitor import ResourceMonitor, ResourceSnapshot

@unittest.skipIf(not os.getenv('TELLME_TEST_MODEL_PATH'), "TELLME_TEST_MODEL_PATH not set")
class TestPerformance(unittest.TestCase):
    def setUp(self):
        self._orig_validate = RuntimeValidator.validate
        self._orig_get_snapshot = ResourceMonitor.get_snapshot
        RuntimeValidator.validate = lambda *args, **kwargs: True
        ResourceMonitor.get_snapshot = lambda: ResourceSnapshot(
            available_ram_mb=64000.0,
            total_ram_mb=64000.0,
            process_ram_mb=100.0,
            cpu_percent=0.0
        )

        model_path = os.getenv('TELLME_TEST_MODEL_PATH')
        assert model_path is not None
        self.model_path = model_path
        self.server_path = os.getenv('TELLME_TEST_LLAMA_SERVER')
        
        self.descriptor = ModelDescriptor(
            id="perf-model",
            display_name="Performance Model",
            path=self.model_path,
            format=ModelFormat.GGUF,
            size_bytes=os.path.getsize(self.model_path) if os.path.exists(self.model_path) else 1000,
            metadata={"general.architecture": "llama", "qwen2.context_length": "4096"}
        )

    def tearDown(self):
        RuntimeValidator.validate = self._orig_validate
        ResourceMonitor.get_snapshot = self._orig_get_snapshot

    def test_local_engine_performance(self):
        manager = RuntimeManager()
        
        load_start = time.time()
        session = manager.load_model(self.descriptor)
        load_time = time.time() - load_start
        
        req = InferenceRequest(prompt="Explain quantum physics in 100 words.", max_tokens=100)
        
        gen_start = time.time()
        generator = session.generate(req)
        
        first_token_time = None
        token_count = 0
        
        for chunk in generator:
            if first_token_time is None:
                first_token_time = time.time()
            token_count += 1
            
        total_time = time.time() - gen_start
        ttft = first_token_time - gen_start if first_token_time else 0
        tps = token_count / total_time if total_time > 0 else 0
        
        manager.unload_model(self.descriptor.id)
        
        print(f"\n[Performance] TellMe Runtime:")
        print(f"  Load Time: {load_time:.2f}s")
        print(f"  TTFT: {ttft:.3f}s")
        print(f"  TPS: {tps:.2f} tokens/sec")
        print(f"  Total Tokens: {token_count}")
        
    @unittest.skipIf(not os.getenv('TELLME_TEST_LLAMA_SERVER'), "TELLME_TEST_LLAMA_SERVER not set")
    def test_llama_server_performance(self):
        # We would launch llama-server and hit its HTTP endpoint here to compare.
        # Implementation left out as it's an external executable and could block the test runner.
        # But the skeleton is here if the user sets TELLME_TEST_LLAMA_SERVER.
        pass
