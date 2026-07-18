import os
from pathlib import Path
from frontend.themes.base_theme import AbstractBaseTheme
from .tokens import make_modern_tokens
from .factory import ModernComponentFactory

class ModernTheme(AbstractBaseTheme):
    """
    Modern Theme: Flat, clean, minimalist design for premium desktop experience.
    """
    @property
    def id(self) -> str:
        return "modern"

    @property
    def tokens(self):
        return make_modern_tokens()

    def get_factory(self, engine):
        return ModernComponentFactory(engine)

    def get_qss_path(self) -> Path:
        """Returns the absolute path to style.qss so ResourceManager can load it."""
        return Path(__file__).parent / "style.qss"

    def on_apply(self, app, engine):
        pass

def get_theme():
    return ModernTheme()
