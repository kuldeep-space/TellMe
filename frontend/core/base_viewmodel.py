
from PySide6.QtCore import QObject, Signal, Property
from frontend.core.app_context import AppContext

class BaseViewModel(QObject):
    """
    Responsibilities: state updates, loading state, error state, logger, cleanup hooks.
    """
    is_loading_changed = Signal(bool)
    error_message_changed = Signal(str)

    def __init__(self, ctx: AppContext, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self.logger = ctx.logger
        self._is_loading = False
        self._error_message = ""

    @Property(bool, notify=is_loading_changed)
    def is_loading(self) -> bool:
        return self._is_loading

    @is_loading.setter
    def is_loading(self, value: bool):
        if self._is_loading != value:
            self._is_loading = value
            self.is_loading_changed.emit(value)

    @Property(str, notify=error_message_changed)
    def error_message(self) -> str:
        return self._error_message

    @error_message.setter
    def error_message(self, value: str):
        if self._error_message != value:
            self._error_message = value
            self.error_message_changed.emit(value)

    def cleanup(self):
        """Hook for cleaning up resources when screen unloads."""
        pass

