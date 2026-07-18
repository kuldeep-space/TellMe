"""
CoreLabel helpers — styled QLabel factory functions and subclass.
"""
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from frontend.engine import StyleEngine

class CoreLabel(QLabel):
    """Base styled terminal label."""

    def __init__(self, text: str = "", engine: StyleEngine = None, parent=None):
        super().__init__(text, parent)
        self.setObjectName("terminalLabel")
        color = "#33ff00"
        if engine:
            color = engine.resolver.resolve_color("colors.text_primary")
            
        self.setStyleSheet(
            f"color: {color}; "
            f"background: transparent; font-size: 14px;"
        )


# ── Factory helpers ──────────────────────────────────────────────────────

def label_h1(text: str, engine: StyleEngine = None, parent=None) -> QLabel:
    lbl = QLabel(text, parent)
    lbl.setObjectName("labelH1")
    color = "#ffffff"
    if engine:
        color = engine.resolver.resolve_color("colors.text_primary")
    lbl.setStyleSheet(f"color: {color}; background: transparent; font-size: 24px; font-weight: bold;")
    return lbl

def label_h2(text: str, engine: StyleEngine = None, parent=None) -> QLabel:
    lbl = QLabel(text, parent)
    lbl.setObjectName("labelH2")
    color = "#ffffff"
    if engine:
        color = engine.resolver.resolve_color("colors.text_primary")
    lbl.setStyleSheet(f"color: {color}; background: transparent; font-size: 18px; font-weight: bold;")
    return lbl

def label_muted(text: str, engine: StyleEngine = None, parent=None) -> QLabel:
    lbl = QLabel(text, parent)
    lbl.setObjectName("labelMuted")
    color = "#456145"
    if engine:
        color = engine.resolver.resolve_color("colors.text_muted")
    lbl.setStyleSheet(f"color: {color}; background: transparent; font-size: 11px;")
    return lbl


def label_secondary(text: str, engine: StyleEngine = None, parent=None) -> QLabel:
    lbl = QLabel(text, parent)
    lbl.setObjectName("labelSecondary")
    color = "#8fd68f"
    if engine:
        color = engine.resolver.resolve_color("colors.text_secondary")
    lbl.setStyleSheet(f"color: {color}; background: transparent; font-size: 12px;")
    return lbl


def label_danger(text: str, engine: StyleEngine = None, parent=None) -> QLabel:
    lbl = QLabel(text, parent)
    lbl.setObjectName("labelDanger")
    color = "#ff3333"
    if engine:
        color = engine.resolver.resolve_color("colors.text_primary") # Use text_primary for danger or status.danger
    lbl.setStyleSheet(f"color: {color}; background: transparent; font-size: 11px;")
    return lbl


def label_success(text: str, engine: StyleEngine = None, parent=None) -> QLabel:
    lbl = QLabel(text, parent)
    lbl.setObjectName("labelSuccess")
    color = "#33ff00"
    if engine:
        color = engine.resolver.resolve_color("status.success")
    lbl.setStyleSheet(f"color: {color}; background: transparent; font-size: 11px;")
    return lbl


def label_warning(text: str, engine: StyleEngine = None, parent=None) -> QLabel:
    lbl = QLabel(text, parent)
    lbl.setObjectName("labelWarning")
    color = "#ffb000"
    if engine:
        color = engine.resolver.resolve_color("status.warning")
    lbl.setStyleSheet(f"color: {color}; background: transparent; font-size: 11px;")
    return lbl
