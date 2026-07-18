"""
TerminalComponentFactory — creates terminal-styled widgets.
"""
from typing import Any
from frontend.engine import StyleEngine
from frontend.themes.base_theme import ButtonVariant, BadgeLevel

# Import the refactored terminal components
from frontend.components.core.core_button import CoreButton
from frontend.components.core.core_input import CoreInput, TerminalTextArea
from frontend.components.core.core_badge import CoreBadge
from frontend.components.core.core_progress import CoreProgress
from frontend.components.core.core_separator import CoreSeparator
from frontend.components.core.core_toggle import CoreToggle
from frontend.components.core.core_statusbar import CoreStatusBar
from frontend.components.core.core_window import CoreWindow
from frontend.components.sidebar.sidebar_widget import TerminalSidebar
from frontend.components.core.core_label import (
    CoreLabel, label_muted, label_secondary, label_danger, label_success, label_warning
)


class TerminalComponentFactory:
    """
    Creates components styled for the Terminal theme.
    """
    def __init__(self, engine: StyleEngine):
        self._engine = engine

    def make_button(self, label: str, variant: ButtonVariant = ButtonVariant.PRIMARY, parent: Any = None) -> Any:
        return CoreButton(label, engine=self._engine, variant=variant, parent=parent)

    def make_input(self, placeholder: str = "", prompt: str = "$ ", parent: Any = None) -> Any:
        return CoreInput(prompt=prompt, placeholder=placeholder, engine=self._engine, parent=parent)

    def make_textarea(self, read_only: bool = False, parent: Any = None) -> Any:
        return TerminalTextArea(parent=parent, read_only=read_only, engine=self._engine)

    def make_badge(self, level: BadgeLevel, parent: Any = None) -> Any:
        return CoreBadge(level=level, engine=self._engine, parent=parent)

    def make_progress(self, width: int = 20, show_percent: bool = True, parent: Any = None) -> Any:
        return CoreProgress(width=width, engine=self._engine, parent=parent, show_percent=show_percent)

    def make_separator(self, char: str = "─", parent: Any = None) -> Any:
        return CoreSeparator(engine=self._engine, char=char, parent=parent)

    def make_toggle(self, initial: bool = False, parent: Any = None) -> Any:
        return CoreToggle(initial=initial, engine=self._engine, parent=parent)

    def make_statusbar(self, parent: Any = None) -> Any:
        return CoreStatusBar(engine=self._engine, parent=parent)

    def make_sidebar(self, parent: Any = None) -> Any:
        # Pass engine if supported, otherwise just instantiate
        return TerminalSidebar(engine=self._engine, parent=parent)

    def make_window(self, title: str = "", accent: bool = False, parent: Any = None) -> Any:
        return CoreWindow(title=title, engine=self._engine, parent=parent, accent=accent)

    def make_label(self, text: str, role: str = "primary", parent: Any = None) -> Any:
        if role == "muted":
            return label_muted(text, engine=self._engine, parent=parent)
        elif role == "secondary":
            return label_secondary(text, engine=self._engine, parent=parent)
        elif role == "danger":
            return label_danger(text, engine=self._engine, parent=parent)
        elif role == "success":
            return label_success(text, engine=self._engine, parent=parent)
        elif role == "warning":
            return label_warning(text, engine=self._engine, parent=parent)
        return CoreLabel(text, engine=self._engine, parent=parent)
