"""
MainWindow — root application window.
Composes: TerminalSidebar | ContentStack (QStackedWidget)
Footer: CoreStatusBar
Overlay: CRTOverlay (rendered on top of everything)
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QStackedWidget
)
from PySide6.QtCore import Qt, QSize
from frontend.core.app_context import AppContext
from frontend.components.core.crt_overlay import CRTOverlay
from frontend.theme.constants import Constants


class MainWindow(QMainWindow):
    def __init__(self, ctx: AppContext):
        super().__init__()
        self.ctx    = ctx
        self.logger = ctx.logger

        self.setWindowTitle("TellMe")
        self.setMinimumSize(Constants.WIN_MIN_WIDTH, Constants.WIN_MIN_HEIGHT)

        # ── Window Icon (Slightly Rounded) ──────────────────────────────
        import os
        from PySide6.QtGui import QIcon, QPixmap, QPainter, QPainterPath
        from PySide6.QtCore import Qt, QRectF
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logos", "Logo-without.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                # Make a square pixmap for best icon results
                dim = min(pixmap.width(), pixmap.height())
                square_pixmap = pixmap.copy((pixmap.width() - dim) // 2, (pixmap.height() - dim) // 2, dim, dim)
                
                rounded = QPixmap(dim, dim)
                rounded.fill(Qt.GlobalColor.transparent)
                
                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                path = QPainterPath()
                radius = dim * 0.25 # Slightly rounded corners
                path.addRoundedRect(QRectF(0, 0, dim, dim), radius, radius)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, square_pixmap)
                painter.end()
                
                self.setWindowIcon(QIcon(rounded))

        # ── Root State Manager ──────────────────────────────────────────
        self.root_stack = QStackedWidget(self)
        self.setCentralWidget(self.root_stack)

        # ── Application Shell (State 1) ─────────────────────────────────
        self.app_shell = QWidget()
        self.app_shell.setObjectName("MainWindowContent")
        self.app_shell.setStyleSheet("QWidget#MainWindowContent { background: transparent; }")
        root_layout = QVBoxLayout(self.app_shell)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Top Bar ────────────────────────────────────────────────────
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(64)
        self.top_bar.setStyleSheet("background: transparent;")
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(16, 16, 16, 0)
        
        # Logo (Left)
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(2)
        
        logo_lbl = ctx.ui.make_label("TELLME", role="h1")
        logo_lbl.setStyleSheet(logo_lbl.styleSheet() + " letter-spacing: 1px;")
        logo_layout.addWidget(logo_lbl)
        
        tagline_lbl = ctx.ui.make_label("Your AI Interview Coach", role="secondary")
        tagline_lbl.setStyleSheet(tagline_lbl.styleSheet() + " font-size: 11px;")
        logo_layout.addWidget(tagline_lbl)
        
        top_bar_layout.addWidget(logo_container)
        
        top_bar_layout.addStretch()
        
        # Greeting (Right)
        self.greeting_lbl = ctx.ui.make_label("Hello, User!", role="secondary")
        self._update_greeting(ctx.profile_service.current_profile)
        ctx.profile_service.profile_updated.connect(self._update_greeting)
        
        top_bar_layout.addWidget(self.greeting_lbl)
        
        root_layout.addWidget(self.top_bar)

        # ── Main row: sidebar + content ────────────────────────────────
        main_row = QWidget()
        row_layout = QHBoxLayout(main_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)

        # Sidebar
        self.sidebar = ctx.ui.make_sidebar()
        row_layout.addWidget(self.sidebar)

        # Content stack
        self.content_stack = QStackedWidget()
        row_layout.addWidget(self.content_stack, stretch=1)

        root_layout.addWidget(main_row, stretch=1)

        # ── Status bar ────────────────────────────────────────────────
        self.status_bar = ctx.ui.make_statusbar()
        root_layout.addWidget(self.status_bar)



        # ── Navigation setup ──────────────────────────────────────────
        self.ctx.navigation_controller.set_stack(self.content_stack)

        # Wire sidebar → nav, nav → sidebar
        self.sidebar.navigation_requested.connect(self.ctx.navigation_controller.push)
        self.ctx.navigation_controller.navigated.connect(self._on_navigated)

        # Init screens (must happen AFTER signals are wired so initial push reflects in UI)
        self._init_screens()

        # ── CRT Overlay (must be last — sits on top of everything) ─────
        if self.ctx.theme_manager.active_theme.id == "industrial":
            self.crt = CRTOverlay(self, scanlines=True, vignette=True, flicker=False)
            self.crt.resize(self.size())
            self.crt.show()

    def _update_greeting(self, profile):
        name = profile.name.strip()
        if name:
            self.greeting_lbl.setText(f"Hello, {name}!")
        else:
            self.greeting_lbl.setText("Hello, Guest!")

    def _init_screens(self):
        nav = self.ctx.navigation_controller

        from frontend.screens.interview_modes.screen  import InterviewModesScreen
        from frontend.screens.interview_config.screen import InterviewConfigScreen
        from frontend.screens.interview.screen  import InterviewScreen
        from frontend.screens.history.screen    import HistoryScreen
        from frontend.screens.report.screen     import ReportScreen
        from frontend.screens.models.screen     import ModelsScreen
        from frontend.screens.settings.screen   import SettingsScreen

        nav.register_screen("interview_modes", InterviewModesScreen(self.ctx, self.content_stack))
        nav.register_screen("interview_config", InterviewConfigScreen(self.ctx, self.content_stack))
        nav.register_screen("interview", InterviewScreen(self.ctx, self.content_stack))
        nav.register_screen("history",   HistoryScreen(self.ctx, self.content_stack))
        nav.register_screen("report",    ReportScreen(self.ctx, self.content_stack))
        nav.register_screen("models",    ModelsScreen(self.ctx, self.content_stack))
        nav.register_screen("settings",  SettingsScreen(self.ctx, self.content_stack))

        from frontend.screens.onboarding.screen import OnboardingScreen
        # Note: onboarding is not part of the main navigation stack
        self.onboarding_screen = OnboardingScreen(self.ctx, self.root_stack)
        self.onboarding_screen.vm.onboarding_completed.connect(self._on_onboarding_completed)
        
        # Add root states
        self.root_stack.addWidget(self.onboarding_screen) # Index 0: Onboarding
        self.root_stack.addWidget(self.app_shell)         # Index 1: AppShell

        if self.ctx.profile_service.requires_onboarding:
            self.root_stack.setCurrentIndex(0)
        else:
            self.root_stack.setCurrentIndex(1)
            self.ctx.profile_service.verify_resume()
            nav.push("interview_modes")
            
    def _on_onboarding_completed(self):
        self.root_stack.setCurrentIndex(1)
        self.ctx.navigation_controller.push("interview_modes")

    def _on_navigated(self, screen_id: str):
        self.sidebar.reflect_navigation(screen_id)
        self.status_bar.set_status("v0.1.0")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "crt"):
            self.crt.resize(self.size())
