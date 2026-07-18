import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock

from backend.core.model_library_service import ModelLibraryService
from backend.domain.models import ModelDescriptor, ModelFormat

class TestImportPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.library_dir = os.path.join(self.temp_dir.name, "library")
        os.makedirs(self.library_dir)
        
        # Create a fake gguf file
        self.fake_model_path = os.path.join(self.temp_dir.name, "source.gguf")
        with open(self.fake_model_path, "w") as f:
            f.write("fake gguf content")
            
    def tearDown(self):
        self.temp_dir.cleanup()
        
    @patch('backend.core.model_library_service.extract_metadata')
    @patch('backend.core.model_library_service.EngineResolver.resolve')
    def test_import_rollback_on_registry_failure(self, mock_resolve, mock_extract):
        mock_resolve.return_value = "llama.cpp"
        
        descriptor = ModelDescriptor(
            id="test", display_name="Test", path="source.gguf", 
            size_bytes=100, format=ModelFormat.GGUF, architecture="test", metadata={}
        )
        mock_extract.return_value = descriptor
        
        # Mock registry
        mock_registry = MagicMock()
        mock_registry.get_managed_models_dir.return_value = self.library_dir
        mock_registry.get_all.return_value = []
        mock_registry.register.side_effect = RuntimeError("Fake registry error")
        
        service = ModelLibraryService(registry=mock_registry)
        
        # Mock registry to raise exception
        service._registry.register = MagicMock(side_effect=RuntimeError("Fake registry error"))
        
        result = service.import_model(self.fake_model_path, copy_to_library=True)
        
        self.assertFalse(result.success)
        self.assertIn("Registration failed", result.error)
        
        # Verify the copied file was rolled back
        copied_files = os.listdir(self.library_dir)
        self.assertEqual(len(copied_files), 0, "Copied file should be removed upon registry failure.")

if __name__ == '__main__':
    unittest.main()
