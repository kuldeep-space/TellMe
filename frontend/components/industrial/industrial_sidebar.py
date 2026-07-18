"""
IndustrialSidebar — Raised steel panel on the left.
"""
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel, QButtonGroup, QFrame
from PySide6.QtCore import Signal, Qt, QUrl
from PySide6.QtGui import QPainter, QDesktopServices, QColor
from frontend.components.base.base_sidebar import BaseSidebar
from frontend.engine import StyleEngine
from frontend.core.navigation import NavigationRegistry, NavigationItem
from frontend.components.industrial.sidebar_nav_item import SidebarNavItem

class IndustrialSidebar(BaseSidebar):
    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(engine, parent)
        self.setFixedWidth(250) # Desktop standard width
        
        # Shell structural layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 32, 16, 24)
        layout.setSpacing(4) # Tight professional grouping
        
        # We removed the sidebar branding to let the MainWindow Top Bar handle it.
        
        # 2. Primary Navigation (Dynamic from Registry)
        self._buttons = {}
        self._current = ""
        
        main_items = NavigationRegistry.get_main_items()
        for item in main_items:
            nav_btn = SidebarNavItem(engine, item)
            nav_btn.clicked.connect(lambda _, sid=item.id: self._on_click(sid))
            layout.addWidget(nav_btn)
            self._buttons[item.id] = nav_btn
            
        # 3. Flexible Spacer
        layout.addStretch(1)
        
        # 4. Secondary Navigation (Settings)
        sub_color = engine.resolver.resolve_qcolor("colors.text_muted").name()
        
        sep1 = QFrame()
        sep1.setFixedHeight(1)
        sep1.setStyleSheet(f"background: {sub_color}; opacity: 0.2; margin: 12px 0px;")
        layout.addWidget(sep1)
        
        settings_item = NavigationItem(id="settings", title="Settings", icon="settings.svg", route="settings", order=90)
        settings_btn = SidebarNavItem(engine, settings_item)
        settings_btn.clicked.connect(lambda: self._on_click("settings"))
        layout.addWidget(settings_btn)
        self._buttons["settings"] = settings_btn
        
        # 5. Footer Identity
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {sub_color}; opacity: 0.2; margin: 12px 0px;")
        layout.addWidget(sep2)
        
        github_item = NavigationItem(id="github", title="Kuldeep", icon="github.svg", route="", order=99)
        github_btn = SidebarNavItem(engine, github_item)
        github_btn.clicked.connect(self._open_github)
        layout.addWidget(github_btn)

    def paintEvent(self, event):
        """Draws the subtle 1px right border for the shell column."""
        painter = QPainter(self)
        # Background is inherited, we just draw the border
        border_color = self.engine.resolver.resolve_qcolor("colors.border")
        # Make the border line clearly visible to separate the sidebar from the page
        border_color.setAlpha(80) # Increased opacity for better visibility
        painter.setPen(border_color)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

    def _open_github(self):
        # Uncheck it immediately since it's just a hyperlink, not a route
        QDesktopServices.openUrl(QUrl("https://github.com/kuldeep-space"))
        # Clear its active state since it's not a real screen
        for sid, btn in self._buttons.items():
            if sid == self._current:
                btn.setChecked(True)
        # Because github_btn isn't in self._buttons, we just need to ensure the group state is fine
        # Oh wait, we didn't use QButtonGroup. SidebarNavItem is just checkable.
        # We handle mutuality manually in _set_active

    def _on_click(self, screen_id: str):
        self.navigation_requested.emit(screen_id)

    def _set_active(self, screen_id: str):
        for sid, btn in self._buttons.items():
            btn.setChecked(sid == screen_id)
        self._current = screen_id

    def reflect_navigation(self, screen_id: str):
        self._set_active(screen_id)
