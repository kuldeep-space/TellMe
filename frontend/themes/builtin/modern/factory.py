"""
Modern ComponentFactory.
"""
from typing import Any
from frontend.engine import StyleEngine
from frontend.themes.base_theme import ButtonVariant, BadgeLevel

from frontend.components.modern.modern_button import ModernButton
from frontend.components.modern.modern_input import ModernInput
from frontend.components.modern.modern_badge import ModernBadge
from frontend.components.modern.modern_progress import ModernProgress
from frontend.components.modern.modern_separator import ModernSeparator
from frontend.components.modern.modern_toggle import ModernToggle
from frontend.components.modern.modern_statusbar import ModernStatusBar
from frontend.components.modern.modern_sidebar import ModernSidebar
from frontend.components.modern.modern_panel import ModernPanel
from frontend.components.base.base_textarea import BaseTextarea
from frontend.components.core.core_label import (
    CoreLabel, label_muted, label_secondary, label_danger, label_success, label_warning, label_h1, label_h2
)

class ModernComponentFactory:
    """
    Creates components styled for the Modern theme.
    """
    def __init__(self, engine: StyleEngine):
        self._engine = engine

    def make_button(self, label: str, variant: ButtonVariant = ButtonVariant.PRIMARY, parent: Any = None) -> Any:
        return ModernButton(engine=self._engine, text=label, variant=variant, parent=parent)

    def make_input(self, placeholder: str = "", prompt: str = "", parent: Any = None) -> Any:
        return ModernInput(engine=self._engine, placeholder=placeholder, prompt=prompt, parent=parent)

    def make_textarea(self, read_only: bool = False, parent: Any = None) -> Any:
        ta = BaseTextarea(engine=self._engine, parent=parent)
        ta.setReadOnly(read_only)
        ta.setObjectName("ModernTextarea") # Hooks into general styling if needed
        return ta

    def make_badge(self, level: BadgeLevel, parent: Any = None) -> Any:
        return ModernBadge(engine=self._engine, text=level.value, level=level, parent=parent)

    def make_progress(self, width: int = 20, show_percent: bool = True, parent: Any = None) -> Any:
        return ModernProgress(engine=self._engine, parent=parent)

    def make_separator(self, char: str = "─", parent: Any = None) -> Any:
        return ModernSeparator(engine=self._engine, horizontal=True, parent=parent)

    def make_toggle(self, initial: bool = False, parent: Any = None) -> Any:
        toggle = ModernToggle(engine=self._engine, parent=parent)
        toggle.setChecked(initial)
        return toggle

    def make_statusbar(self, parent: Any = None) -> Any:
        return ModernStatusBar(engine=self._engine, parent=parent)

    def make_sidebar(self, parent: Any = None) -> Any:
        return ModernSidebar(engine=self._engine, parent=parent)

    def make_window(self, title: str = "", accent: bool = False, parent: Any = None) -> Any:
        panel = ModernPanel(engine=self._engine, parent=parent)
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
