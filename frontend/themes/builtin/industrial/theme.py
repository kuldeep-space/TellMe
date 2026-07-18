"""
Industrial Theme Plugin Initialization.
"""
from frontend.themes.base_theme import AbstractBaseTheme
from frontend.themes.builtin.industrial.factory import IndustrialComponentFactory
from frontend.themes.builtin.industrial.tokens import INDUSTRIAL_TOKENS
from pathlib import Path

_THEME_DIR = Path(__file__).parent

class IndustrialTheme(AbstractBaseTheme):
    @property
    def id(self) -> str:
        return "industrial"
        
    @property
    def name(self) -> str:
        return "Industrial"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def tokens(self) -> dict:
        return INDUSTRIAL_TOKENS
        
    def get_qss_path(self) -> Path:
        return _THEME_DIR / "style.qss"
        
    def get_factory(self, engine):
        return IndustrialComponentFactory(engine)
        
    def get_settings_widget(self) -> type:
        from frontend.themes.builtin.industrial.settings import IndustrialSettings
        return IndustrialSettings

    def on_apply(self, app, engine) -> None:
        pass


_instance: IndustrialTheme | None = None

def get_theme() -> IndustrialTheme:
    global _instance
    if _instance is None:
        _instance = IndustrialTheme()
    return _instance
