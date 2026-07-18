"""
ThemeRegistry — discovers and registers theme plugins.
"""
from pathlib import Path
from frontend.themes.base_theme import AbstractBaseTheme, ThemeManifest
from backend.core.logging import get_logger

_logger = get_logger(__name__)

class ThemeRegistry:
    """Registry for all available themes."""
    
    _instance: "ThemeRegistry | None" = None

    def __new__(cls) -> "ThemeRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registry = {}
        return cls._instance

    def register(self, theme: AbstractBaseTheme):
        if not theme.id:
            _logger.error(f"Cannot register theme with no ID: {theme}")
            return
        
        self._registry[theme.id] = theme
        _logger.info(f"Theme registered: {theme.id}")

    def get(self, theme_id: str) -> AbstractBaseTheme | None:
        return self._registry.get(theme_id)

    def list_all(self) -> list[ThemeManifest]:
        return [t.manifest for t in self._registry.values() if t.manifest]

    def list_themes(self) -> list[str]:
        return list(self._registry.keys())

    def auto_discover(self, search_dirs: list[Path]):
        import importlib
        import sys
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            for theme_dir in search_dir.iterdir():
                if not theme_dir.is_dir():
                    continue
                
                manifest_path = theme_dir / "manifest.json"
                if not manifest_path.exists():
                    continue
                    
                try:
                    manifest = ThemeManifest.from_json(manifest_path)
                except Exception as e:
                    _logger.warning(f"Failed to parse manifest {manifest_path}: {e}")
                    continue
                    
                # Import the theme module
                # e.g., themes/builtin/terminal -> frontend.themes.builtin.terminal.theme
                module_path = f"frontend.themes.{search_dir.name}.{theme_dir.name}.theme"
                try:
                    if module_path not in sys.modules:
                        importlib.import_module(module_path)
                    
                    # Assume the module has a get_theme() function that returns the instance
                    module = sys.modules[module_path]
                    if hasattr(module, "get_theme"):
                        theme = module.get_theme()
                        theme.manifest = manifest
                        self.register(theme)
                    else:
                        _logger.warning(f"Module {module_path} does not export get_theme()")
                except Exception as e:
                    _logger.error(f"Failed to import theme {module_path}: {e}")
