"""
Terminal Component Library
All reusable terminal-native UI widgets for TellMe.

Components:
  CoreWindow      — bordered pane with ASCII header
  CoreButton      — [ COMMAND ] style button
  CoreInput       — shell-prompt prefixed input
  CoreProgress    — ASCII block progress bar
  TerminalTable       — fixed-width tabular output
  CoreLabel       — styled monospace label variants
  CoreSeparator   — horizontal dashed separator line
  CoreBadge       — inline status badge (OK / ERR / WARN)
  CoreToggle      — on/off switch rendered as [ON] / [OFF]
"""
from .core_window import CoreWindow
from .core_button import CoreButton, CoreButtonDanger, CoreButtonWarning
from .core_input import CoreInput, TerminalTextArea
from .core_progress import CoreProgress
from .core_label import CoreLabel, label_muted, label_secondary, label_danger, label_success, label_warning
from .core_separator import CoreSeparator
from .core_badge import CoreBadge, BadgeLevel
from .core_toggle import CoreToggle

__all__ = [
    "CoreWindow",
    "CoreButton", "CoreButtonDanger", "CoreButtonWarning",
    "CoreInput", "TerminalTextArea",
    "CoreProgress",
    "CoreLabel", "label_muted", "label_secondary",
    "label_danger", "label_success", "label_warning",
    "CoreSeparator",
    "CoreBadge", "BadgeLevel",
    "CoreToggle",
]
