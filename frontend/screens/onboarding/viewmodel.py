from PySide6.QtCore import Property, Signal, Slot
from frontend.core.base_viewmodel import BaseViewModel
from frontend.core.app_context import AppContext
import os

class OnboardingViewModel(BaseViewModel):
    error_changed = Signal(str)
    onboarding_completed = Signal()

    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(ctx, parent)
        self._error = ""

    @Property(str, notify=error_changed)
    def error(self) -> str:
        return self._error

    @error.setter
    def error(self, value: str):
        if self._error != value:
            self._error = value
            self.error_changed.emit(value)

    @Slot(str, str)
    def submit_profile(self, name: str, resume_path: str):
        name = name.strip()
        if not name:
            self.error = "Name is required to initialize your profile."
            return

        if resume_path:
            resume_path = resume_path.strip()
            if not os.path.exists(resume_path):
                self.error = "The provided resume path does not exist."
                return

        # Clear error
        self.error = ""
        
        # Save profile
        self.ctx.profile_service.update_profile(name=name, resume_path=resume_path)
        
        # Signal completion
        self.onboarding_completed.emit()

    @Slot(str)
    def skip_resume_and_submit(self, name: str):
        self.submit_profile(name, "")
