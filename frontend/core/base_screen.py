
from PySide6.QtWidgets import QWidget
from frontend.core.app_context import AppContext

class BaseScreen(QWidget):
    """
    Provides lifecycle methods, logger, access to NavigationController and UI Store.
    """
    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self.logger = ctx.logger
        self.nav = ctx.navigation_controller
        self.store = ctx.store

    def on_enter(self):
        self.logger.debug(f"{self.__class__.__name__} on_enter")

    def on_leave(self):
        self.logger.debug(f"{self.__class__.__name__} on_leave")

    def on_pause(self):
        self.logger.debug(f"{self.__class__.__name__} on_pause")

    def on_resume(self):
        self.logger.debug(f"{self.__class__.__name__} on_resume")

