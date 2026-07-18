import os
import unittest
import threading
from typing import List

from backend.core.runtime.manager import RuntimeManager
from backend.domain.models import ModelDescriptor, InferenceResponse, ModelFormat
from backend.core.runtime.models import InferenceRequest
from backend.core.runtime.events import RuntimeEvent, EventBus, ModelLoaded, GenerationStarted, GenerationFinished, DiagnosticsUpdated, ModelUnloaded
from backend.core.runtime.validator import RuntimeValidator
from backend.core.runtime.monitor import ResourceMonitor, ResourceSnapshot

# Note: this test requires an actual GGUF model path set in TELLME_TEST_MODEL_PATH
# e.g., export TELLME_TEST_MODEL_PATH="d:\models\qwen-1.5b-q4.gguf"

@unittest.skipIf(not os.getenv('TELLME_TEST_MODEL_PATH'), "TELLME_TEST_MODEL_PATH not set")
class TestRuntimeManagerE2E(unittest.TestCase):
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
        self.events_received: List[RuntimeEvent] = []
        
        # Subscribe to EventBus
        def on_event(event: RuntimeEvent):
            self.events_received.append(event)
            
        EventBus.subscribe(on_event)
        
    def tearDown(self):
        # Ensure cleanup
        self.manager.shutdown()
        
        # Verify clean state
        self.assertEqual(self.manager.active_session_count(), 0)
        self.assertEqual(len(self.manager._engines), 0)
        
        EventBus._subscribers.clear()
        RuntimeValidator.validate = self._orig_validate
        ResourceMonitor.get_snapshot = self._orig_get_snapshot

    def test_e2e_load_generate_unload(self):
        # 1. Mock Descriptor (we won't run extract_metadata to avoid coupling, just hardcode what we need)
        descriptor = ModelDescriptor(
            id="test-e2e-model",
            display_name="Test E2E",
            path=self.model_path,
            format=ModelFormat.GGUF,
            size_bytes=os.path.getsize(self.model_path) if os.path.exists(self.model_path) else 1000,
            metadata={"general.architecture": "llama", "qwen2.context_length": "4096"}
        )
        
        # 2. Load
        session = self.manager.load_model(descriptor)
        self.assertIsNotNone(session, "Failed to create session")
        self.assertEqual(session.plan.model_id, descriptor.id)
        
        # Verify ModelLoaded event
        loaded_events = [e for e in self.events_received if isinstance(e, ModelLoaded)]
        self.assertTrue(len(loaded_events) > 0, "ModelLoaded event not emitted")
        
        # 3. Generate
        req = InferenceRequest(prompt="Hello, world!", max_tokens=5)
        generator = session.generate(req)
        
        responses = []
        for chunk in generator:
            responses.append(chunk)
            
        self.assertTrue(len(responses) > 0, "No tokens generated")
        
        # Verify events
        gen_started = [e for e in self.events_received if isinstance(e, GenerationStarted)]
        gen_finished = [e for e in self.events_received if isinstance(e, GenerationFinished)]
        diag_updated = [e for e in self.events_received if isinstance(e, DiagnosticsUpdated)]
        
        self.assertTrue(len(gen_started) > 0, "GenerationStarted not emitted")
        self.assertTrue(len(gen_finished) > 0, "GenerationFinished not emitted")
        self.assertTrue(len(diag_updated) > 0, "DiagnosticsUpdated not emitted")
        
        # Verify actual vs requested context in diagnostics
        last_diag = diag_updated[-1].diagnostics
        self.assertIsNotNone(last_diag.actual_context)
        self.assertIsNotNone(last_diag.actual_memory_mb)
        
        # 4. Unload
        self.manager.unload_model("test-e2e-model")
        unloaded_events = [e for e in self.events_received if isinstance(e, ModelUnloaded)]
        self.assertTrue(len(unloaded_events) > 0, "ModelUnloaded not emitted")
        
        # Verify clean state
        self.assertEqual(self.manager.active_session_count(), 0)
        
        # Verify event sequence ordering
        event_types = [type(e) for e in self.events_received]
        expected_sequence = [ModelLoaded, DiagnosticsUpdated, GenerationStarted, GenerationFinished, ModelUnloaded]
        filtered_events = [t for t in event_types if t in expected_sequence]
        self.assertEqual(filtered_events, expected_sequence, f"Incorrect event sequence: {filtered_events}")
