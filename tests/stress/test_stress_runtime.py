import os
import gc
import psutil
import unittest
import threading
import time
from typing import List

from backend.core.runtime.manager import RuntimeManager
from backend.domain.models import ModelDescriptor, ModelFormat
from backend.core.runtime.models import InferenceRequest
from backend.core.runtime.events import RuntimeEvent, EventBus
from backend.core.runtime.validator import RuntimeValidator
from backend.core.runtime.monitor import ResourceMonitor, ResourceSnapshot

@unittest.skipIf(not os.getenv('TELLME_TEST_MODEL_PATH'), "TELLME_TEST_MODEL_PATH not set")
class TestRuntimeManagerStress(unittest.TestCase):
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
        self.manager = RuntimeManager()
        EventBus._subscribers.clear()
        self.process = psutil.Process(os.getpid())
        gc.collect()
        self.base_memory = self.process.memory_info().rss

    def tearDown(self):
        self.manager.shutdown()
        RuntimeValidator.validate = self._orig_validate
        ResourceMonitor.get_snapshot = self._orig_get_snapshot
        
        # Verify no orphan threads (other than main and test threads)
        # In a real environment, we'd check thread counts carefully.
        
        # Verify memory returns to baseline (allow 50MB fuzz factor for python allocations)
        gc.collect()
        final_memory = self.process.memory_info().rss
        memory_diff_mb = (final_memory - self.base_memory) / (1024 * 1024)
        
        self.assertLess(memory_diff_mb, 50, f"Memory leak detected: {memory_diff_mb:.2f} MB not reclaimed")
        self.assertEqual(self.manager.active_session_count(), 0, "Orphaned RuntimeSessions remain")
        self.assertEqual(len(self.manager._engines), 0, "Lingering engines remain")
        self.assertEqual(len(EventBus._subscribers), 0, "Lingering EventBus subscribers remain")
        
        EventBus._subscribers.clear()

    def test_repeated_load_unload(self):
        descriptor = ModelDescriptor(
            id="stress-model-1",
            display_name="Stress Model",
            path=self.model_path,
            format=ModelFormat.GGUF,
            size_bytes=os.path.getsize(self.model_path) if os.path.exists(self.model_path) else 1000,
            metadata={"general.architecture": "llama", "qwen2.context_length": "4096"}
        )
        
        iterations = int(os.getenv('TELLME_STRESS_ITERATIONS', 5))
        for i in range(iterations):
            session = self.manager.load_model(descriptor)
            self.assertIsNotNone(session)
            self.manager.unload_model(descriptor.id)
            
            # Assert cleanup per iteration
            self.assertIsNone(self.manager.find_session(descriptor.id))

    def test_mid_generation_cancellation(self):
        descriptor = ModelDescriptor(
            id="stress-model-2",
            display_name="Stress Model 2",
            path=self.model_path,
            format=ModelFormat.GGUF,
            size_bytes=os.path.getsize(self.model_path) if os.path.exists(self.model_path) else 1000,
            metadata={"general.architecture": "llama", "qwen2.context_length": "4096"}
        )
        
        session = self.manager.load_model(descriptor)
        req = InferenceRequest(prompt="Write a very long essay.", max_tokens=500)
        
        generator = session.generate(req)
        
        # Pull 2 tokens then cancel
        tokens = []
        for i, chunk in enumerate(generator):
            tokens.append(chunk)
            if i == 2:
                session.cancel()
                break
                
        # Give it a tiny bit of time to cancel the backend
        time.sleep(0.5)
        
        self.assertEqual(session.state.value, "Cancelling", "Session state should be cancelled")
        self.manager.unload_model(descriptor.id)
