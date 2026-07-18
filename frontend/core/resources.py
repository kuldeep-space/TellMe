"""
ResourceManager — centralized cache for icons, pixmaps, fonts, textures, and QSS.
All assets are loaded once and served from cache on subsequent requests.
"""
from pathlib import Path
from typing import Dict, Optional
from PySide6.QtGui import QIcon, QPixmap, QFontDatabase, QFont
from PySide6.QtCore import QObject
from backend.core.logging import get_logger

_logger = get_logger(__name__)


class ResourceManager(QObject):
    """
    Centralized cache for all assets (Icons, Images, Fonts, QSS, Textures).
    Avoids repeatedly reading files from disk.

    Public API:
        get_icon(name)        → QIcon
        get_pixmap(name)      → QPixmap
        get_texture(name)     → QPixmap  (from assets/textures/)
        get_qss(name)         → str      (raw template, not hydrated)
        load_font(filename)   → int      (font DB id)
        verify_fonts(families)→ dict[str, bool]
        ensure_textures_dir() → Path
        print_stats()
    """

    def __init__(self, assets_dir: Path):
        super().__init__()
        self.assets_dir    = assets_dir
        self.icons_dir     = assets_dir / "icons"
        self.fonts_dir     = assets_dir / "fonts"
        self.textures_dir  = assets_dir / "textures"

        # Caches
        self._icon_cache:    Dict[str, QIcon]   = {}
        self._pixmap_cache:  Dict[str, QPixmap] = {}
        self._texture_cache: Dict[str, QPixmap] = {}
        self._style_cache:   Dict[str, str]     = {}
        self._font_ids:      Dict[str, int]     = {}

        # Stats
        self.stats = {"hits": 0, "misses": 0}

    # ------------------------------------------------------------------ #
    # Icons
    # ------------------------------------------------------------------ #
    def get_icon(self, icon_name: str) -> QIcon:
        """Load and cache an SVG icon by filename."""
        if icon_name in self._icon_cache:
            self.stats["hits"] += 1
            return self._icon_cache[icon_name]

        self.stats["misses"] += 1
        icon_path = self.icons_dir / icon_name
        if not icon_path.exists():
            _logger.warning(f"Icon not found: {icon_path}")
            return QIcon()

        icon = QIcon(str(icon_path))
        self._icon_cache[icon_name] = icon
        return icon

    # ------------------------------------------------------------------ #
    # Pixmaps / Images
    # ------------------------------------------------------------------ #
    def get_pixmap(self, image_name: str) -> QPixmap:
        """Load and cache a QPixmap (logos, images)."""
        if image_name in self._pixmap_cache:
            self.stats["hits"] += 1
            return self._pixmap_cache[image_name]

        self.stats["misses"] += 1
        for subdir in ["logos", ""]:
            image_path = (
                self.assets_dir / subdir / image_name if subdir
                else self.assets_dir / image_name
            )
            if image_path.exists():
                pixmap = QPixmap(str(image_path))
                self._pixmap_cache[image_name] = pixmap
                return pixmap

        _logger.warning(f"Image not found: {image_name}")
        return QPixmap()

    # ------------------------------------------------------------------ #
    # Textures (tiles for noise, carbon, etc.)
    # ------------------------------------------------------------------ #
    def get_texture(self, name: str) -> QPixmap:
        """
        Load and cache a texture tile pixmap from assets/textures/.
        Returns empty QPixmap if not found (caller should generate and save it first).
        """
        if name in self._texture_cache:
            self.stats["hits"] += 1
            return self._texture_cache[name]

        self.stats["misses"] += 1
        path = self.textures_dir / name
        if not path.exists():
            _logger.debug(f"Texture not yet generated: {path}")
            return QPixmap()

        pix = QPixmap(str(path))
        self._texture_cache[name] = pix
        _logger.info(f"Texture loaded: {name} ({pix.width()}×{pix.height()})")
        return pix

    def store_texture(self, name: str, pixmap: QPixmap) -> bool:
        """
        Save a generated texture pixmap to assets/textures/ and cache it.
        Returns True on success.
        """
        self.ensure_textures_dir()
        path = self.textures_dir / name
        ok = pixmap.save(str(path), "PNG")
        if ok:
            self._texture_cache[name] = pixmap
            _logger.info(f"Texture saved: {path}")
        else:
            _logger.warning(f"Texture save failed: {path}")
        return ok

    def ensure_textures_dir(self) -> Path:
        """Create assets/textures/ if it does not exist."""
        self.textures_dir.mkdir(parents=True, exist_ok=True)
        return self.textures_dir

    # ------------------------------------------------------------------ #
    # Stylesheets (raw template text — not yet hydrated)
    # ------------------------------------------------------------------ #
    def get_qss(self, style_name: str) -> str:
        """Load and cache a QSS template file from assets/ or an absolute path."""
        if style_name in self._style_cache:
            self.stats["hits"] += 1
            return self._style_cache[style_name]

        self.stats["misses"] += 1

        # Try absolute path first (theme packages pass their own path)
        p = Path(style_name)
        if p.is_absolute() and p.exists():
            qss_path = p
        else:
            qss_path = self.assets_dir / style_name
            if not qss_path.exists():
                _logger.error(f"Stylesheet not found: {qss_path}")
                return ""

        with open(qss_path, "r", encoding="utf-8") as f:
            content = f.read()

        self._style_cache[style_name] = content
        return content

    def invalidate_qss(self, style_name: str):
        """Remove a cached QSS entry so it is reloaded on next get_qss()."""
        self._style_cache.pop(style_name, None)

    # ------------------------------------------------------------------ #
    # Fonts
    # ------------------------------------------------------------------ #
    def load_font(self, font_filename: str) -> int:
        """
        Load a font file from assets/fonts/ into QFontDatabase.
        Returns the font ID (or -1 on failure). Cached so file is only read once.
        """
        if font_filename in self._font_ids:
            self.stats["hits"] += 1
            return self._font_ids[font_filename]

        self.stats["misses"] += 1
        fp = self.fonts_dir / font_filename
        if not fp.exists():
            _logger.warning(f"Font file not found: {fp}")
            self._font_ids[font_filename] = -1
            return -1

        fid = QFontDatabase.addApplicationFont(str(fp))
        self._font_ids[font_filename] = fid
        if fid >= 0:
            families = QFontDatabase.applicationFontFamilies(fid)
            _logger.info(f"Font registered: {font_filename} -> {families}")
        else:
            _logger.warning(f"Font failed to register: {font_filename}")
        return fid

    def verify_fonts(self, families: list) -> dict:
        """
        Check whether each font family name is registered in QFontDatabase.

        Returns:
            dict[str, bool] — {family_name: is_registered}

        Logs a warning for each missing family so the developer knows
        which fallback chains will be active.
        """
        result = {}
        db_families = QFontDatabase.families()
        for family in families:
            found = any(family.lower() in f.lower() for f in db_families)
            result[family] = found
            if not found:
                _logger.warning(
                    f"Font family '{family}' not registered — system fallback will be used."
                )
            else:
                _logger.info(f"Font family '{family}': OK")
        return result

    # ------------------------------------------------------------------ #
    # Diagnostics
    # ------------------------------------------------------------------ #
    def print_stats(self):
        _logger.info(
            f"ResourceManager Cache Stats — "
            f"Hits: {self.stats['hits']}, Misses: {self.stats['misses']}"
        )
