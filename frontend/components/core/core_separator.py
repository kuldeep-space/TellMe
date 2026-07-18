"""
CoreSeparator — horizontal dashed/solid line separator.
"""
from frontend.components.base.base_separator import BaseSeparator
from frontend.engine import StyleEngine

class CoreSeparator(BaseSeparator):
    """Renders a dashed separator line."""

    def __init__(self, engine: StyleEngine = None, char: str = "─", parent=None):
        super().__init__(engine, True, parent)
        self.setObjectName("terminalSeparator")
        
        if engine is None:
            self.setStyleSheet(
                "QFrame#terminalSeparator { border-top: 1px dashed #1f521f; border-bottom: none; }"
            )
