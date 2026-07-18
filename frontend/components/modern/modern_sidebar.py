from PySide6.QtWidgets import QVBoxLayout, QWidget, QFrame
from PySide6.QtCore import Signal, QUrl
from PySide6.QtGui import QPainter, QDesktopServices, QColor
from frontend.components.base.base_sidebar import BaseSidebar
from frontend.engine import StyleEngine
from frontend.core.navigation import NavigationRegistry, NavigationItem
from frontend.components.industrial.sidebar_nav_item import SidebarNavItem
from frontend.components.modern.sidebar_sub_item import SidebarSubItem
from frontend.state.draft_model import InterviewDraft
from typing import Optional

class ModernSidebar(BaseSidebar):
    draft_close_requested = Signal(str)
    draft_clicked = Signal(str)

    def __init__(self, engine: StyleEngine, parent=None):
        super().__init__(engine, parent)
        self.setFixedWidth(250)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 80, 16, 24)
        layout.setSpacing(4)
        
        self._buttons = {}
        self._current = ""
        self._draft_items = {} # Maps draft_id -> SidebarSubItem
        self._nav_layout = layout
        self._drafts = {}
        self._active_draft_id = None
        
        main_items = NavigationRegistry.get_main_items()
        for item in main_items:
            # Re-using SidebarNavItem but styled via QSS for modern theme
            nav_btn = SidebarNavItem(engine, item)
            nav_btn.clicked.connect(lambda _, sid=item.id: self._on_click(sid))
            layout.addWidget(nav_btn)
            self._buttons[item.id] = nav_btn
            
        layout.addStretch(1)
        
        sub_color = engine.resolver.resolve_qcolor("colors.text_muted").name()
        
        sep1 = QFrame()
        sep1.setFixedHeight(1)
        sep1.setStyleSheet(f"background: {sub_color}; opacity: 0.1; margin: 12px 0px;")
        layout.addWidget(sep1)
        
        self._settings_mode = False
        self._settings_sub_items = []
        
        settings_item = NavigationItem(id="settings", title="Settings", icon="settings.svg", route="settings", order=90)
        self.settings_btn = SidebarNavItem(engine, settings_item)
        self.settings_btn.clicked.connect(self._toggle_settings_mode)
        layout.addWidget(self.settings_btn)
        self._buttons["settings"] = self.settings_btn
        
        # Settings Sub-items (Hidden by default)
        self._settings_sub_items_map = {}
        
        profile_item = SidebarSubItem(engine, "Profile", closable=False)
        profile_item.clicked.connect(lambda: self.navigation_requested.emit("settings_profile"))
        profile_item.hide()
        layout.addWidget(profile_item)
        self._settings_sub_items.append(profile_item)
        self._settings_sub_items_map["settings_profile"] = profile_item
        
        model_item = SidebarSubItem(engine, "Model Settings", closable=False)
        model_item.clicked.connect(lambda: self.navigation_requested.emit("settings_model"))
        model_item.hide()
        layout.addWidget(model_item)
        self._settings_sub_items.append(model_item)
        self._settings_sub_items_map["settings_model"] = model_item
        
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {sub_color}; opacity: 0.1; margin: 12px 0px;")
        layout.addWidget(sep2)
        
        github_item = NavigationItem(id="github", title="Kuldeep-space", icon="github.svg", route="", order=99)
        github_btn = SidebarNavItem(engine, github_item)
        github_btn.clicked.connect(self._open_github)
        layout.addWidget(github_btn)

    def _toggle_settings_mode(self):
        self._settings_mode = not self._settings_mode
        if self._settings_mode:
            # Entering Settings Mode
            self.settings_btn.item.title = "Close"
            self.settings_btn.set_icon("close.svg")
            self.settings_btn.update()
            for item in self._settings_sub_items:
                item.show()
            self.navigation_requested.emit("settings")
        else:
            # Exiting Settings Mode
            self.settings_btn.item.title = "Settings"
            self.settings_btn.set_icon("settings.svg")
            self.settings_btn.update()
            for item in self._settings_sub_items:
                item.hide()
            self.navigation_requested.emit("settings_close")

    def deactivate_settings_mode(self):
        if self._settings_mode:
            self._settings_mode = False
            self.settings_btn.item.title = "Settings"
            self.settings_btn.set_icon("settings.svg")
            self.settings_btn.update()
            for item in self._settings_sub_items:
                item.hide()

    def paintEvent(self, event):
        """Very subtle or no border for modern theme."""
        painter = QPainter(self)
        border_color = self.engine.resolver.resolve_qcolor("colors.border")
        border_color.setAlpha(40) # Extremely subtle border
        painter.setPen(border_color)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

    def _open_github(self):
        QDesktopServices.openUrl(QUrl("https://github.com/kuldeep-space"))
        for sid, btn in self._buttons.items():
            if sid == self._current:
                btn.setChecked(True)

    def _on_click(self, screen_id: str):
        self.navigation_requested.emit(screen_id)

    def _set_active(self, screen_id: str):
        for sid, btn in self._buttons.items():
            btn.setChecked(sid == screen_id)
                
        if hasattr(self, '_settings_sub_items_map'):
            for sid, item in self._settings_sub_items_map.items():
                item.set_active(sid == screen_id)
                
        self._current = screen_id

    def reflect_navigation(self, screen_id: str):
        self._set_active(screen_id)

    def on_drafts_changed(self, drafts: dict):
        self._drafts = drafts
        
        for item in self._draft_items.values():
            self._nav_layout.removeWidget(item)
            item.deleteLater()
        self._draft_items.clear()
        
        # Find the 'interview_modes' button index
        insert_idx = -1
        for i in range(self._nav_layout.count()):
            item = self._nav_layout.itemAt(i)
            if item and item.widget() == self._buttons.get("interview_modes"):
                insert_idx = i + 1
                break
                
        if insert_idx == -1:
            insert_idx = self._nav_layout.count()

        # Add active drafts
        # Iterate in sorted order or just as they appear
        for draft_id, draft in drafts.items():
            if draft.status == 'active' and (not draft.is_empty or draft_id == self._active_draft_id):
                sub_item = SidebarSubItem(self.engine, draft.title)
                
                # We need to capture draft_id safely in lambda
                sub_item.clicked.connect(lambda did=draft_id: self.draft_clicked.emit(did))
                sub_item.close_requested.connect(lambda did=draft_id: self.draft_close_requested.emit(did))
                
                self._draft_items[draft_id] = sub_item
                self._nav_layout.insertWidget(insert_idx, sub_item)
                insert_idx += 1
                
    def on_active_draft_id_changed(self, active_id: str):
        self._active_draft_id = active_id
        if hasattr(self, '_drafts'):
            self.on_drafts_changed(self._drafts)
