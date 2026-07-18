"""
StyleEngine — The single point of contact between themes and widgets.
"""
from PySide6.QtCore import QObject
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import QWidget
from typing import Any

from frontend.engine.token_resolver import TokenResolver
from frontend.engine.theme_cache import ThemeCache
from frontend.engine.animation_manager import AnimationManager
from backend.core.logging import get_logger

_logger = get_logger(__name__)

class StyleEngine(QObject):
    """
    Provides all styling capabilities (fonts, icons, animations, qpainter styling).
    Widgets use this to apply their appearance.
    """
    def __init__(self, resolver: TokenResolver, cache: ThemeCache, anim: AnimationManager, parent: QObject | None = None):
        super().__init__(parent)
        self._resolver = resolver
        self._cache = cache
        self._anim = anim
        
    @property
    def resolver(self) -> TokenResolver:
        return self._resolver
        
    @property
    def cache(self) -> ThemeCache:
        return self._cache
        
    @property
    def anim(self) -> AnimationManager:
        return self._anim

    def apply_font(self, widget: QWidget, family_token: str, size_token: str, weight_token: str):
        """Applies font to a widget by resolving tokens."""
        family = self._resolver.resolve_str(family_token)
        # Assuming family token gives a comma-separated list like "Inter, sans-serif"
        # QFont prefers a single primary family, but accepts comma separated in setFamilies
        primary = family.split(",")[0].strip()
        
        size = self._resolver.resolve_int(size_token)
        weight = self._resolver.resolve_int(weight_token)
        
        # Convert CSS weight to QFont::Weight (0-99). QFont.Weight is typically 400->QFont.Normal, 700->QFont.Bold
        # In Qt6, QFont.Weight enum maps roughly: 400=Normal(50), 700=Bold(75). 
        # Actually QFont.Weight(int) takes 0-99. 400 is CSS, Qt uses 1-999 in QFont constructor? 
        # Qt6 setWeight takes an int matching CSS weights (e.g. 400, 700).
        font = QFont()
        font.setFamilies([f.strip() for f in family.split(",")])
        if size > 0:
            font.setPointSize(size)
        if weight > 0:
            font.setWeight(QFont.Weight(weight))
            
        widget.setFont(font)

    def recolor_icon(self, icon: QIcon, color: str) -> QIcon:
        # TODO: Implement SVG recoloring via QPainter if needed.
        # For now, return as is. The cache will handle recolored variants.
        return icon

    def get_applied_tokens(self, widget: QWidget) -> dict[str, Any]:
        """For the Design Inspector."""
        # This would reverse map widget properties to tokens if we track them,
        # but for now we just dump the resolver.
        return self._resolver.dump()
