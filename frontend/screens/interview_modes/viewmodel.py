"""
Dashboard ViewModel — system monitor / diagnostics state.
"""
from frontend.core.base_viewmodel import BaseViewModel
from backend.domain.interview_mode import InterviewRegistry

class InterviewModesViewModel(BaseViewModel):
    def get_interview_categories(self):
        """Returns modes grouped by category."""
        return InterviewRegistry.get_by_category()

    def get_all_modes(self):
        """Returns all modes flat."""
        return InterviewRegistry.get_all()

    def start_interview_mode(self, mode_id: str):
        """Dispatches the selected mode to the setup wizard."""
        self.ctx.store.active_interview_mode = mode_id
        self.ctx.navigation_controller.push("setup")

    def go_to_history(self):
        self.ctx.navigation_controller.push("history")

    def go_to_models(self):
        self.ctx.navigation_controller.push("models")

    def go_to_settings(self):
        self.ctx.navigation_controller.push("settings")

    def go_to_report(self):
        self.ctx.navigation_controller.push("report")
