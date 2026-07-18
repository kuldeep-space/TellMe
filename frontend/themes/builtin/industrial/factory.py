"""
Industrial ComponentFactory.
"""
from typing import Any
from frontend.engine import StyleEngine
from frontend.themes.base_theme import ButtonVariant, BadgeLevel

# Import the industrial components
from frontend.components.industrial.industrial_button import IndustrialButton
from frontend.components.industrial.industrial_input import IndustrialInput
from frontend.components.industrial.industrial_badge import IndustrialBadge
from frontend.components.industrial.industrial_progress import IndustrialProgress
from frontend.components.industrial.industrial_separator import IndustrialSeparator
from frontend.components.industrial.industrial_toggle import IndustrialToggle
from frontend.components.industrial.industrial_statusbar import IndustrialStatusBar
from frontend.components.industrial.industrial_sidebar import IndustrialSidebar
from frontend.components.industrial.steel_panel import SteelPanel
from frontend.components.base.base_textarea import BaseTextarea
from frontend.components.core.core_label import (
    CoreLabel, label_muted, label_secondary, label_danger, label_success, label_warning, label_h1, label_h2
)

class IndustrialComponentFactory:
    """
    Creates components styled for the Industrial theme.
    """
    def __init__(self, engine: StyleEngine):
        self._engine = engine

    def make_button(self, label: str, variant: ButtonVariant = ButtonVariant.PRIMARY, parent: Any = None) -> Any:
        return IndustrialButton(engine=self._engine, text=label, variant=variant, parent=parent)

    def make_input(self, placeholder: str = "", prompt: str = "", parent: Any = None) -> Any:
        # Industrial input ignores prompt, but we can respect it if we want.
        # For now just use IndustrialInput directly.
        return IndustrialInput(engine=self._engine, placeholder=placeholder, parent=parent)

    def make_textarea(self, read_only: bool = False, parent: Any = None) -> Any:
        # We can just use BaseTextarea, maybe wrapped in a ScanlineScreen if we wanted,
        # but let's stick to a styled BaseTextarea.
        ta = BaseTextarea(engine=self._engine, parent=parent)
        ta.setReadOnly(read_only)
        return ta

    def make_badge(self, level: BadgeLevel, parent: Any = None) -> Any:
        return IndustrialBadge(engine=self._engine, text=level.value, level=level, parent=parent)

    def make_progress(self, width: int = 20, show_percent: bool = True, parent: Any = None) -> Any:
        return IndustrialProgress(engine=self._engine, parent=parent)

    def make_separator(self, char: str = "─", parent: Any = None) -> Any:
        return IndustrialSeparator(engine=self._engine, horizontal=True, parent=parent)

    def make_toggle(self, initial: bool = False, parent: Any = None) -> Any:
        toggle = IndustrialToggle(engine=self._engine, parent=parent)
        toggle.setChecked(initial)
        return toggle

    def make_statusbar(self, parent: Any = None) -> Any:
        return IndustrialStatusBar(engine=self._engine, parent=parent)

    def make_sidebar(self, parent: Any = None) -> Any:
        return IndustrialSidebar(engine=self._engine, parent=parent)

    def make_window(self, title: str = "", accent: bool = False, parent: Any = None) -> Any:
        # Steel panel acts as a window
        panel = SteelPanel(engine=self._engine, elevation="panel", parent=parent, screws=True)
        if title:
            lbl = label_secondary(title, engine=self._engine, parent=panel)
            panel.add_widget(lbl)
            panel.add_widget(self.make_separator())
        return panel

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
        elif role == "h1":
            return label_h1(text, engine=self._engine, parent=parent)
        elif role == "h2":
            return label_h2(text, engine=self._engine, parent=parent)
        return CoreLabel(text, engine=self._engine, parent=parent)
