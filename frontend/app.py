"""
TellMe Desktop Application — Entry Point
Bootstraps backend, initializes PySide6, loads fonts, applies theme, shows window.
"""
import sys
import traceback
from pathlib import Path
from PySide6.QtWidgets import QApplication, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from backend.app.bootstrap import bootstrap
from backend.app.lifecycle import ApplicationLifecycle
from backend.core.logging import get_logger

from frontend.core.app_context import AppContext
from frontend.core.resources import ResourceManager
from frontend.core.theme import ThemeManager
from frontend.core.navigation import NavigationController
from frontend.core.profile_service import ProfileService
from frontend.state.store import UIStore
from frontend.views.main_window import MainWindow

_logger = get_logger("frontend.app")


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Handle uncaught frontend exceptions with logging + dialog."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    _logger.critical(f"Uncaught exception:\n{error_msg}")

    try:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("ERR — TellMe Critical Failure")
        msg_box.setText("FATAL: Uncaught exception.")
        msg_box.setInformativeText(str(exc_value))
        msg_box.setDetailedText(error_msg)
        msg_box.exec()
    except Exception:
        pass


# Ordered font registration — Inter first (Industrial theme), then JetBrains Mono (Terminal)
_FONT_FILES = [
    ("Inter-Regular.ttf",      "Inter"),
    ("Inter-Medium.ttf",       "Inter"),
    ("Inter-SemiBold.ttf",     "Inter"),
    ("Inter-Bold.ttf",         "Inter"),
    ("JetBrainsMonoNL-Regular.ttf", "JetBrains Mono"),
    ("JetBrainsMonoNL-Bold.ttf",    "JetBrains Mono"),
]


def _load_fonts(resource_manager: ResourceManager, assets_dir: Path) -> str:
    """
    Register all bundled fonts with QFontDatabase.
    Inter: sans-serif for Industrial and future themes.
    JetBrains Mono: monospace for Terminal theme and all data labels.
    Returns the primary mono font family name (used as the app-wide default).
    """
    mono_family = None
    for font_file, _ in _FONT_FILES:
        fid = resource_manager.load_font(font_file)
        if fid >= 0 and mono_family is None and "Mono" in font_file:
            from PySide6.QtGui import QFontDatabase
            fams = QFontDatabase.applicationFontFamilies(fid)
            if fams:
                mono_family = fams[0]

    if mono_family is None:
        mono_family = "Consolas"
        _logger.warning("JetBrains Mono not loaded; falling back to Consolas")

    # Verification report
    font_report = resource_manager.verify_fonts(["Inter", "JetBrains Mono"])
    for family, ok in font_report.items():
        if ok:
            _logger.info(f"Font family '{family}': registered OK")
        else:
            _logger.warning(f"Font family '{family}': NOT FOUND — system fallback active")

    return mono_family


def main() -> int:
    """Main entry point for the TellMe desktop application."""
    import time
    t0 = time.time()

    # Fix Windows Taskbar icon (must be called before QApplication)
    if sys.platform == "win32":
        import ctypes
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "tellme.terminal.v0.1"
            )
        except Exception:
            pass

    # High DPI — pass-through scaling (Qt6 default)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    sys.excepthook = global_exception_handler

    # ── Backend bootstrap ──────────────────────────────────────────────
    try:
        container = bootstrap()
        lifecycle = ApplicationLifecycle(container)
        lifecycle.startup()
    except Exception as e:
        _logger.critical(f"Backend bootstrap failed: {e}")
        return 1

    try:
        # ── QApplication ──────────────────────────────────────────────
        app = QApplication(sys.argv)
        app.setApplicationName("TellMe")

        # ── Resource Manager ──────────────────────────────────────────
        t_res = time.time()
        assets_dir = Path(__file__).parent / "assets"
        resource_manager = ResourceManager(assets_dir)

        # ── Font Loading (must happen before stylesheet) ───────────────
        primary_font_family = _load_fonts(resource_manager, assets_dir)
        from frontend.theme.typography import Typography
        Typography.FAMILY_PRIMARY = primary_font_family

        # Set application-wide default font
        default_font = QFont(primary_font_family, 12)
        app.setFont(default_font)

        # ── UIStore, ThemeManager, NavigationController ────────────────
        store = UIStore()
        theme_manager = ThemeManager()
        theme_manager._registry.auto_discover([Path(__file__).parent / "themes" / "builtin"])
        nav_controller = NavigationController()
        profile_service = ProfileService()
        
        from frontend.state.draft_manager import DraftManager
        draft_manager = DraftManager(store)

        app_context = AppContext(
            resource_manager=resource_manager,
            theme_manager=theme_manager,
            navigation_controller=nav_controller,
            profile_service=profile_service,
            store=store,
            draft_manager=draft_manager,
        )
        t_res_end = time.time()

        # ── Apply Theme (loads QSS, hydrates tokens) ───────────────────
        t_theme = time.time()
        theme_manager.apply_theme("modern")
        t_theme_end = time.time()

        # ── Set window icon and Taskbar Icon ───────────────────────────
        if sys.platform == "win32":
            import ctypes
            myappid = 'tellme.app.version0.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
        logo = resource_manager.get_pixmap("Logo.png")
        if not logo.isNull():
            from PySide6.QtGui import QIcon, QPixmap, QPainter, QPainterPath
            from PySide6.QtCore import QRectF
            
            rounded = QPixmap(logo.size())
            rounded.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, logo.width(), logo.height()), 5, 5)
            
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, logo)
            painter.end()
            
            app.setWindowIcon(QIcon(rounded))

        # ── MainWindow ─────────────────────────────────────────────────
        t_nav = time.time()
        window = MainWindow(app_context)
        window.showMaximized()
        t_nav_end = time.time()

        # ── Performance Report ─────────────────────────────────────────
        _logger.info(f"Resource init:     {(t_res_end - t_res)*1000:.1f} ms")
        _logger.info(f"Theme loading:     {(t_theme_end - t_theme)*1000:.1f} ms")
        _logger.info(f"Window init:       {(t_nav_end - t_nav)*1000:.1f} ms")
        _logger.info(f"Total startup:     {(time.time() - t0)*1000:.1f} ms")
        _logger.info(f"Font family:       {primary_font_family}")
        resource_manager.print_stats()
        _logger.info("TellMe terminal UI initialized. READY.")

        # ── Event Loop ────────────────────────────────────────────────
        exit_code = app.exec()
        return exit_code

    except Exception as e:
        _logger.critical(f"Fatal frontend error: {e}")
        traceback.print_exc()
        return 1
    finally:
        _logger.info("Shutting down...")
        try:
            lifecycle.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
