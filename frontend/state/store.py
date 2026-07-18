
from PySide6.QtCore import QObject, Signal, Property

class UIStore(QObject):
    """
    Observable state container for centralized UI state.
    Widgets should react to state changes instead of polling values.
    """
    theme_changed = Signal(str)
    sidebar_expanded_changed = Signal(bool)
    theme_preview_active_changed = Signal(bool)
    preview_theme_id_changed = Signal(str)
    active_interview_mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_theme = "terminal"
        self._sidebar_expanded = True
        self._theme_preview_active = False
        self._preview_theme_id = ""
        self._active_interview_mode = ""
        
    @Property(str, notify=theme_changed)
    def current_theme(self) -> str:
        return self._current_theme
        
    @current_theme.setter
    def current_theme(self, value: str):
        if self._current_theme != value:
            self._current_theme = value
            self.theme_changed.emit(value)

    @Property(bool, notify=sidebar_expanded_changed)
    def sidebar_expanded(self) -> bool:
        return self._sidebar_expanded
        
    @sidebar_expanded.setter
    def sidebar_expanded(self, value: bool):
        if self._sidebar_expanded != value:
            self._sidebar_expanded = value
            self.sidebar_expanded_changed.emit(value)

    @Property(bool, notify=theme_preview_active_changed)
    def theme_preview_active(self) -> bool:
        return self._theme_preview_active
        
    @theme_preview_active.setter
    def theme_preview_active(self, value: bool):
        if self._theme_preview_active != value:
            self._theme_preview_active = value
            self.theme_preview_active_changed.emit(value)

    @Property(str, notify=preview_theme_id_changed)
    def preview_theme_id(self) -> str:
        return self._preview_theme_id
        
    @preview_theme_id.setter
    def preview_theme_id(self, value: str):
        if self._preview_theme_id != value:
            self._preview_theme_id = value
            self.preview_theme_id_changed.emit(value)

    @Property(str, notify=active_interview_mode_changed)
    def active_interview_mode(self) -> str:
        return self._active_interview_mode
        
    @active_interview_mode.setter
    def active_interview_mode(self, value: str):
        if self._active_interview_mode != value:
            self._active_interview_mode = value
            self.active_interview_mode_changed.emit(value)

