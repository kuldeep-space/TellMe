"""
Setup ViewModel.
"""
from frontend.core.base_viewmodel import BaseViewModel


class SetupViewModel(BaseViewModel):
    def __init__(self, ctx, parent=None):
        super().__init__(ctx, parent)
        self.resume_path    = ""
        self.job_title      = ""
        self.company        = ""
        self.interview_type = "Behavioral"

    def go_back(self):
        self.ctx.navigation_controller.push("dashboard")

    def begin_interview(self):
        self.ctx.navigation_controller.push("interview")
        return True
