from frontend.core.base_viewmodel import BaseViewModel


class InterviewViewModel(BaseViewModel):
    def __init__(self, ctx, parent=None):
        super().__init__(ctx, parent)
        self.mic_active   = False
        self.token_count  = 0
        self.session_id   = ""
        self.is_paused    = False

    def end_session(self):
        self.ctx.navigation_controller.push("report")
