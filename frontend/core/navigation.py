from dataclasses import dataclass, field
from typing import Optional, Callable
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget
from backend.core.logging import get_logger

_logger = get_logger(__name__)

@dataclass
class NavigationItem:
    id: str
    title: str
    icon: str
    route: str
    order: int
    visibility: str = "visible"
    badge_support: bool = False
    permissions: list[str] = field(default_factory=list)
    enabled: bool = True

class NavigationRegistry:
    """Registry containing all navigational elements for the Application Shell."""
    
    _items: list[NavigationItem] = [
        NavigationItem(id="interview_modes", title="Interview Modes", icon="interview.svg", route="interview_modes", order=1),
        NavigationItem(id="report", title="Reports", icon="report.svg", route="report", order=2),
        NavigationItem(id="history", title="History", icon="history.svg", route="history", order=3),
        NavigationItem(id="interview_resume", title="Resume Interview (Dev)", icon="settings.svg", route="interview_resume", order=80),
        NavigationItem(id="interview_behavioral", title="Behavioral Interview (Dev)", icon="settings.svg", route="interview_behavioral", order=81),
        NavigationItem(id="interview_technical", title="Technical Interview (Dev)", icon="settings.svg", route="interview_technical", order=82),
    ]
    
    @classmethod
    def get_main_items(cls) -> list[NavigationItem]:
        return sorted([i for i in cls._items if i.visibility == "visible"], key=lambda x: x.order)

    @classmethod
    def register_item(cls, item: NavigationItem):
        cls._items.append(item)

class NavigationController(QObject):
    """
    Supports push(), replace(), back(), clear_history().
    Manages screen switching and lifecycle events.
    """
    navigated = Signal(str) # Emits screen name

    def __init__(self, stacked_widget: Optional[QStackedWidget] = None):
        super().__init__()
        self.stack = stacked_widget
        self.history: list[str] = []
        self.screens: dict[str, int] = {}
        self.screen_factories: dict[str, Callable] = {}
        
    def set_stack(self, stacked_widget: QStackedWidget):
        self.stack = stacked_widget
        
    def register_screen(self, name: str, widget_or_factory):
        if self.stack is None:
            _logger.error(f"Cannot register screen {name}: stack is not set.")
            return
        if callable(widget_or_factory):
            self.screen_factories[name] = widget_or_factory
            _logger.debug(f"Registered screen factory for {name}")
        else:
            idx = self.stack.addWidget(widget_or_factory)
            self.screens[name] = idx
            _logger.debug(f"Registered screen {name} at index {idx}")

    def push(self, name: str):
        if self.stack is None:
            _logger.error(f"Cannot navigate to {name}: stack is not set.")
            return
            
        if name not in self.screens and name not in self.screen_factories:
            _logger.error(f"Cannot navigate to unknown screen: {name}")
            return
            
        if name not in self.screens and name in self.screen_factories:
            _logger.info(f"Lazily instantiating screen: {name}")
            try:
                widget = self.screen_factories[name]()
                idx = self.stack.addWidget(widget)
                self.screens[name] = idx
                _logger.debug(f"Instantiated and registered screen {name} at index {idx}")
            except Exception as e:
                _logger.exception(f"Failed to instantiate screen {name}: {e}")
                return
            
        # Trigger lifecycle on_leave for current
        current_idx = self.stack.currentIndex()
        if current_idx >= 0:
            current_widget = self.stack.widget(current_idx)
            if hasattr(current_widget, "on_leave"):
                current_widget.on_leave()

        # Trigger lifecycle on_enter for new
        new_idx = self.screens[name]
        self.stack.setCurrentIndex(new_idx)
        self.history.append(name)
        
        new_widget = self.stack.widget(new_idx)
        if hasattr(new_widget, "on_enter"):
            new_widget.on_enter()
            
        _logger.info(f"Navigated to {name}")
        self.navigated.emit(name)
        
    def replace(self, name: str):
        if self.history:
            self.history.pop()
        self.push(name)

    def back(self):
        if len(self.history) > 1:
            self.history.pop() # remove current
            prev = self.history.pop() # get previous
            self.push(prev)
            
    def clear_history(self):
        self.history.clear()

