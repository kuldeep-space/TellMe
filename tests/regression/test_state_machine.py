import os
import unittest

from backend.core.runtime.manager import RuntimeManager
from backend.domain.models import ModelDescriptor, ModelFormat
from backend.core.runtime.models import InferenceRequest
from backend.core.runtime.validator import RuntimeValidator
from backend.core.runtime.monitor import ResourceMonitor, ResourceSnapshot

@unittest.skipIf(not os.getenv('TELLME_TEST_MODEL_PATH'), "TELLME_TEST_MODEL_PATH not set")
class TestStateMachine(unittest.TestCase):
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
        self.descriptor = ModelDescriptor(
            id="state-machine-model",
            display_name="State Machine Model",
            path=self.model_path,
            format=ModelFormat.GGUF,
            size_bytes=os.path.getsize(self.model_path) if os.path.exists(self.model_path) else 1000,
            metadata={"general.architecture": "llama", "qwen2.context_length": "4096"}
        )

    def tearDown(self):
        self.manager.shutdown()
        RuntimeValidator.validate = self._orig_validate
        ResourceMonitor.get_snapshot = self._orig_get_snapshot

    def test_generate_before_load(self):
        # We don't have a session object if it's not loaded via manager, 
        # but what if we get one manually and it's not loaded?
        # Actually, RuntimeManager acts as the gatekeeper. 
        # But if we try to generate with an unloaded session:
        session = self.manager.load_model(self.descriptor)
        self.manager.unload_model(self.descriptor.id)
        
        req = InferenceRequest(prompt="Hello", max_tokens=10)
        with self.assertRaises(RuntimeError) as context:
            list(session.generate(req))
            
        self.assertIn("cannot generate from state", str(context.exception).lower())

    def test_double_load(self):
        session1 = self.manager.load_model(self.descriptor)
        # Loading the same model ID again should just return the existing session or raise an error depending on policy
        # Currently RuntimeManager raises a ValueError if we try to load a model that's already loaded, or it returns the active session.
        # Let's check RuntimeManager behavior.
        
        # In our implementation, loading an active session returns the existing session.
        session2 = self.manager.load_model(self.descriptor)
        self.assertIs(session1, session2)

    def test_double_unload(self):
        self.manager.load_model(self.descriptor)
        
        # First unload should succeed
        self.manager.unload_model(self.descriptor.id)
        
        # Second unload should log a warning but not crash
        self.manager.unload_model(self.descriptor.id)
        
        # Verify it's not in the active sessions
        self.assertIsNone(self.manager.find_session(self.descriptor.id))
