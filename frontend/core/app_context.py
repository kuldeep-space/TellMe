
from dataclasses import dataclass
from typing import Any
from frontend.core.resources import ResourceManager
from frontend.core.theme import ThemeManager
from frontend.core.navigation import NavigationController
from frontend.core.profile_service import ProfileService
from frontend.state.store import UIStore
from frontend.state.draft_manager import DraftManager
from backend.core.logging import get_logger

@dataclass
class AppContext:
    """
    Central access point for frontend-wide services.
    Passed to BaseScreen and BaseViewModel.
    """
    resource_manager: ResourceManager
    theme_manager: ThemeManager
    navigation_controller: NavigationController
    profile_service: ProfileService
    store: UIStore
    draft_manager: DraftManager
    logger: Any = get_logger("frontend.app_context")

    @property
    def ui(self):
        """
        Syntactic sugar to access the active theme's ComponentFactory.
        e.g., `ctx.ui.make_button(...)`
        """
        return self.theme_manager.active_theme.get_factory(self.theme_manager._engine)
