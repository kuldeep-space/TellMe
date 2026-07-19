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
from frontend.components.modern.dialogs import ModernMessageDialog


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
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logos", "Logo.png")
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
        self.workspace_stack = QStackedWidget()
        row_layout.addWidget(self.workspace_stack, stretch=1)
        
        self.content_stack = QStackedWidget()
        self.workspace_stack.addWidget(self.content_stack)
        
        from frontend.screens.settings.settings_panel import SettingsPanel
        self.settings_panel = SettingsPanel(self.ctx)
        self.workspace_stack.addWidget(self.settings_panel)

        root_layout.addWidget(main_row, stretch=1)

        # ── Status bar ────────────────────────────────────────────────
        self.status_bar = ctx.ui.make_statusbar()
        root_layout.addWidget(self.status_bar)

        # ── Navigation setup ──────────────────────────────────────────
        self.ctx.navigation_controller.set_stack(self.content_stack)

        # Wire sidebar → nav, nav → sidebar
        self.sidebar.navigation_requested.connect(self._on_navigation_requested)
        self.ctx.navigation_controller.navigated.connect(self._on_navigated)

        # Wire draft integration if sidebar supports it
        if hasattr(self.sidebar, "on_drafts_changed"):
            self.ctx.store.drafts_changed.connect(self.sidebar.on_drafts_changed)
            self.sidebar.on_drafts_changed(self.ctx.store.drafts)
        if hasattr(self.sidebar, "draft_close_requested"):
            self.sidebar.draft_close_requested.connect(self._on_draft_close_requested)
        if hasattr(self.sidebar, "draft_clicked"):
            self.sidebar.draft_clicked.connect(self._on_draft_clicked)
        if hasattr(self.sidebar, "on_active_draft_id_changed"):
            self.ctx.store.active_draft_id_changed.connect(self.sidebar.on_active_draft_id_changed)

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
            
    def _on_draft_close_requested(self, draft_id: str):
        draft = self.ctx.draft_manager.get_draft(draft_id)
        if draft and draft.has_unsaved_changes:
            dialog = ModernMessageDialog(
                "Delete Draft",
                f"Are you sure you want to delete your {draft.title} draft? Any unsaved progress will be lost.",
                self
            )
            dialog.add_button("Keep Draft", role="secondary")
            dialog.add_button("Delete", role="danger")
            dialog.exec()
            
            if dialog.clicked_button != "Delete":
                return
                
        # If the deleted draft is the one currently opened, navigate away
        is_active = (self.ctx.store.active_draft_id == draft_id)
        
        self.ctx.draft_manager.delete_draft(draft_id)
        
        # If currently on the config screen viewing THIS draft, navigate away
        if is_active and self.ctx.navigation_controller.history and self.ctx.navigation_controller.history[-1] == "interview_config":
            self.ctx.navigation_controller.replace("interview_modes")

    def _on_draft_clicked(self, draft_id: str):
        self.ctx.draft_manager.set_active_draft(draft_id)
        self.ctx.navigation_controller.push("interview_config")

    def _init_screens(self):
        nav = self.ctx.navigation_controller

        # Lazily register screen creators to minimize start-up cost
        def get_interview_modes():
            from frontend.screens.interview_modes.screen import InterviewModesScreen
            return InterviewModesScreen(self.ctx, self.content_stack)
            
        def get_interview_config():
            from frontend.screens.interview_config.screen import InterviewConfigScreen
            return InterviewConfigScreen(self.ctx, self.content_stack)
            
        def get_interview():
            from frontend.screens.interview.screen import InterviewScreen
            return InterviewScreen(self.ctx, self.content_stack)
            
        def get_history():
            from frontend.screens.history.screen import HistoryScreen
            return HistoryScreen(self.ctx, self.content_stack)
            
        def get_report():
            from frontend.screens.report.screen import ReportScreen
            return ReportScreen(self.ctx, self.content_stack)
            
        def get_models():
            from frontend.screens.models.screen import ModelsScreen
            return ModelsScreen(self.ctx, self.content_stack)
            
        def get_settings():
            from frontend.screens.settings.screen import SettingsScreen
            return SettingsScreen(self.ctx, self.content_stack)

        nav.register_screen("interview_modes", get_interview_modes)
        nav.register_screen("interview_config", get_interview_config)
        nav.register_screen("interview", get_interview)
        nav.register_screen("history",   get_history)
        nav.register_screen("report",    get_report)
        nav.register_screen("models",    get_models)
        nav.register_screen("settings",  get_settings)

        # Add root states
        self.root_stack.addWidget(self.app_shell)

        if self.ctx.profile_service.requires_onboarding:
            from frontend.screens.onboarding.screen import OnboardingScreen
            self.onboarding_screen = OnboardingScreen(self.ctx, self.root_stack)
            self.onboarding_screen.vm.onboarding_completed.connect(self._on_onboarding_completed)
            self.root_stack.addWidget(self.onboarding_screen)
            self.root_stack.setCurrentWidget(self.onboarding_screen)
        else:
            self.root_stack.setCurrentWidget(self.app_shell)
            self.ctx.profile_service.verify_resume()
            nav.push("interview_modes")

        # ── Startup Model Pre-load ─────────────────────────────────────
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, self._preload_active_model)
            
    def _preload_active_model(self):
        """Asynchronously pre-loads the selected model in the background at startup."""
        import json
        import os
        from backend.config.settings import get_settings
        from backend.core.tasks import TaskManager
        from backend.core.model_registry import ModelRegistry
        from backend.core.model_runtime import ModelRuntime

        config_path = os.path.join(get_settings().runtime_path, "model_config.json")
        if not os.path.exists(config_path):
            return

        try:
            with open(config_path, "r") as f:
                cfg = json.load(f)
            selected_model_id = cfg.get("selected_model_id")
            if not selected_model_id:
                return

            registry = ModelRegistry.get_instance()
            descriptor = registry.get(selected_model_id)
            if not descriptor:
                self.logger.warning(f"Startup Pre-load: Model '{selected_model_id}' not found in registry.")
                return

            runtime = ModelRuntime.get_instance()
            if runtime.active_model_id == descriptor.id:
                return  # Already loaded

            self.status_bar.set_status(f"PRE-LOADING: {descriptor.display_name}")
            
            # Load global runtime config
            runtime_cfg_path = os.path.join(get_settings().runtime_path, "runtime_config.json")
            runtime_config = {}
            if os.path.exists(runtime_cfg_path):
                with open(runtime_cfg_path, "r") as f:
                    runtime_config = json.load(f)

            def _preload_worker(worker=None):
                runtime.load_model(descriptor, runtime_config)

            task_manager = TaskManager.get_instance()
            task_id = task_manager.submit(_preload_worker, worker=None)
            worker = task_manager.get_worker(task_id)
            if worker:
                def _on_success(t_id, res):
                    self.status_bar.set_status("READY")
                def _on_error(t_id, err):
                    self.status_bar.set_status("LOAD ERROR")
                    self.logger.error(f"Startup Pre-load failed: {err}")
                worker.signals.result.connect(_on_success)
                worker.signals.error.connect(_on_error)


        except Exception as e:
            self.logger.error(f"Failed to set up startup model pre-load: {e}")

    def _on_onboarding_completed(self):
        self.root_stack.setCurrentWidget(self.app_shell)
        self.ctx.navigation_controller.push("interview_modes")

    def _on_navigation_requested(self, screen_id: str):
        if screen_id in ["interview_resume", "interview_behavioral", "interview_technical"]:
            mode_map = {
                "interview_resume": "resume_interview",
                "interview_behavioral": "behavioral_interview",
                "interview_technical": "technical_interview"
            }
            self.ctx.store.active_interview_mode = mode_map[screen_id]
            if self.workspace_stack.currentIndex() == 1:
                if not self.settings_panel.attempt_close():
                    return
                self.workspace_stack.setCurrentIndex(0)
                if hasattr(self.sidebar, "deactivate_settings_mode"):
                    self.sidebar.deactivate_settings_mode()
            self.ctx.navigation_controller.push("interview")
            return

        if screen_id == "settings":
            self.workspace_stack.setCurrentIndex(1)
            self.settings_panel.show_page("profile")
            if hasattr(self, "sidebar"):
                self.sidebar.reflect_navigation("settings_profile")
        elif screen_id == "settings_profile":
            self.settings_panel.show_page("profile")
            if hasattr(self, "sidebar"):
                self.sidebar.reflect_navigation("settings_profile")
        elif screen_id == "settings_model":
            self.settings_panel.show_page("model_settings")
            if hasattr(self, "sidebar"):
                self.sidebar.reflect_navigation("settings_model")
        elif screen_id == "settings_close":
            if self.settings_panel.attempt_close():
                self.workspace_stack.setCurrentIndex(0)
                if hasattr(self.sidebar, "deactivate_settings_mode"):
                    self.sidebar.deactivate_settings_mode()
            else:
                # User cancelled close, so we need to stay in settings mode
                if not self.sidebar._settings_mode:
                    self.sidebar._toggle_settings_mode()
        else:
            # Check if settings is currently open
            if self.workspace_stack.currentIndex() == 1:
                if not self.settings_panel.attempt_close():
                    # If unsaved changes prevent closing, just return
                    return
                self.workspace_stack.setCurrentIndex(0)
                if hasattr(self.sidebar, "deactivate_settings_mode"):
                    self.sidebar.deactivate_settings_mode()
                    
            self.ctx.navigation_controller.push(screen_id)

    def _on_navigated(self, screen_id: str):
        if screen_id == "interview":
            mode = self.ctx.store.active_interview_mode
            mode_to_route = {
                "resume_interview": "interview_resume",
                "behavioral_interview": "interview_behavioral",
                "technical_interview": "interview_technical"
            }
            route = mode_to_route.get(mode, "interview_modes")
            self.sidebar.reflect_navigation(route)
        else:
            self.sidebar.reflect_navigation(screen_id)
            
        self.status_bar.set_status("v0.1.0")
        if screen_id not in ["interview_config", "interview"]:
            self.ctx.draft_manager.set_active_draft(None)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "crt"):
            self.crt.resize(self.size())
