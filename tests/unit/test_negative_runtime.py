import os
import unittest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

from backend.domain.models import ModelDescriptor, ModelFormat, RuntimeStatus
from backend.core.runtime.manager import RuntimeManager
from backend.core.runtime.models import RuntimePlan, InferenceRequest, SessionState
from backend.core.runtime.events import EventBus, ModelLoaded, RuntimeErrorEvent
from backend.core.model_runtime import ModelRuntime
from backend.providers.engines.llama_cpp_engine import LlamaCppEngine, LlamaCppSession

class TestRuntimeNegativeScenarios(unittest.TestCase):
    def setUp(self):
        self.manager = RuntimeManager()
        self.descriptor = ModelDescriptor(
            id="test-negative-model",
            display_name="Test Negative Model",
            path="non_existent_model_path.gguf",
            format=ModelFormat.GGUF,
            size_bytes=1000,
            metadata={"general.architecture": "llama", "qwen2.context_length": "4096"}
        )
        EventBus._subscribers.clear()

    def tearDown(self):
        self.manager.shutdown()
        # Verify clean up after shutdown
        self.assertEqual(self.manager.active_session_count(), 0)
        self.assertEqual(len(self.manager._engines), 0)
        EventBus._subscribers.clear()

    def test_generate_before_loading(self):
        """Verify that attempting to generate before a model is loaded raises RuntimeError."""
        runtime = ModelRuntime()
        req = InferenceRequest(prompt="Hello", max_tokens=5)
        with self.assertRaises(RuntimeError) as ctx:
            runtime.get_generator(req)
        self.assertIn("No model is currently loaded", str(ctx.exception))

    def test_load_same_session_twice(self):
        """Verify that loading the same model descriptor twice returns the identical session."""
        # Mock the engine's actual model load to avoid needing a GGUF file
        # We also mock the validator to bypass the file existence and accessibility checks
        with patch('backend.core.runtime.validator.os.path.isfile', return_value=True), \
             patch('backend.core.runtime.validator.os.access', return_value=True), \
             patch('backend.core.runtime.validator.os.path.getsize', return_value=1000), \
             patch('llama_cpp.Llama') as mock_llama:
            session1 = self.manager.load_model(self.descriptor)
            self.assertIsNotNone(session1)
            
            session2 = self.manager.load_model(self.descriptor)
            self.assertIs(session1, session2, "Subsequent load of same model ID must reuse existing session")
            self.assertEqual(self.manager.active_session_count(), 1)

    def test_unload_twice(self):
        """Verify that unloading a model twice is a clean, silent no-op on the second call."""
        with patch('backend.core.runtime.validator.os.path.isfile', return_value=True), \
             patch('backend.core.runtime.validator.os.access', return_value=True), \
             patch('backend.core.runtime.validator.os.path.getsize', return_value=1000), \
             patch('llama_cpp.Llama') as mock_llama:
            session = self.manager.load_model(self.descriptor)
            self.assertIsNotNone(session)
            
            # First unload
            self.manager.unload_model(self.descriptor.id)
            self.assertEqual(self.manager.active_session_count(), 0)
            
            # Second unload should not raise any exceptions
            try:
                self.manager.unload_model(self.descriptor.id)
            except Exception as e:
                self.fail(f"Unloading a model twice raised an unexpected exception: {e}")

    def test_cancel_after_completion(self):
        """Verify that calling cancel on a session that is not generating is a safe no-op."""
        with patch('backend.core.runtime.validator.os.path.isfile', return_value=True), \
             patch('backend.core.runtime.validator.os.access', return_value=True), \
             patch('backend.core.runtime.validator.os.path.getsize', return_value=1000), \
             patch('llama_cpp.Llama') as mock_llama:
            session = self.manager.load_model(self.descriptor)
            self.assertEqual(session.state, SessionState.READY)
            
            # Cancel while READY (not generating) should be safe
            try:
                session.cancel()
            except Exception as e:
                self.fail(f"Cancelling a non-generating session raised an unexpected exception: {e}")
            self.assertEqual(session.state, SessionState.READY)

    def test_missing_model_file(self):
        """Verify that loading a model with a non-existent file path fails with FileNotFoundError."""
        with self.assertRaises(FileNotFoundError) as ctx:
            self.manager.load_model(self.descriptor)
        self.assertIn("Model file not found", str(ctx.exception))

    def test_corrupted_model_file(self):
        """Verify that loading a corrupted model file fails cleanly."""
        # Create a dummy empty/corrupted file
        corrupt_file_path = "corrupt_test_model.gguf"
        with open(corrupt_file_path, "w") as f:
            f.write("corrupted file content")
        
        corrupted_descriptor = ModelDescriptor(
            id="corrupt-model",
            display_name="Corrupt Model",
            path=corrupt_file_path,
            format=ModelFormat.GGUF,
            size_bytes=10,
            metadata={"general.architecture": "llama", "qwen2.context_length": "512"}
        )
        
        try:
            with self.assertRaises(RuntimeError) as ctx:
                self.manager.load_model(corrupted_descriptor)
            self.assertIn("Failed to create llama_context", str(ctx.exception))
        finally:
            if os.path.exists(corrupt_file_path):
                os.remove(corrupt_file_path)

    def test_invalid_runtime_plan(self):
        """Verify that instantiating a session with an invalid plan fails or sets state to FAILED."""
        # We can construct a plan that will cause llama.cpp to throw (e.g. invalid context length or negative parameters)
        invalid_plan = RuntimePlan(
            engine_id="llama.cpp",
            backend_version="1.0.0",
            model_id="invalid-plan-model",
            model_path="non_existent.gguf",
            architecture="llama",
            context_length=-100, # Invalid negative context length
            batch_size=512,
            ubatch_size=512,
            thread_count=4,
            thread_batch_count=4,
            gpu_layers=0,
            estimated_memory_mb=100.0,
            available_memory_mb=1000.0,
            safety_margin_mb=50.0,
            use_mmap=True,
            use_mlock=False,
            use_flash_attention=False,
            context_reduced=False
        )
        
        session = LlamaCppSession(invalid_plan)
        with self.assertRaises(RuntimeError):
            session.load()
        self.assertEqual(session.state, SessionState.FAILED)
