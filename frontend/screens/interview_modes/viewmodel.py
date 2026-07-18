"""
Dashboard ViewModel — system monitor / diagnostics state.
"""
from frontend.components.modern.dialogs import ModernMessageDialog, ModernListDialog
from frontend.core.base_viewmodel import BaseViewModel
from backend.domain.interview_mode import InterviewRegistry

class InterviewModesViewModel(BaseViewModel):
    def get_interview_categories(self):
        """Returns modes grouped by category."""
        return InterviewRegistry.get_by_category()

    def get_all_modes(self):
        """Returns all modes flat."""
        return InterviewRegistry.get_all()

    def start_interview_mode(self, mode_id: str):
        """Dispatches the selected mode to the setup wizard."""
        active_drafts = self.ctx.draft_manager.get_active_drafts_for_mode(mode_id)
        mode = InterviewRegistry.get(mode_id)
        mode_title = mode.title if mode else "Interview"
        
        if not active_drafts:
            # Create a new draft
            new_draft = self.ctx.draft_manager.create_draft(mode_id, mode_title)
            self.ctx.draft_manager.set_active_draft(new_draft.draft_id)
            self.ctx.store.active_interview_mode = mode_id  # fallback property
            self.ctx.navigation_controller.push("interview_config")
            return

        # Drafts exist, prompt the user
        dialog = ModernMessageDialog(
            "Existing Drafts Found",
            f"You already have existing {mode_title} drafts.",
            self.parent()
        )
        
        dialog.add_button("Resume Existing", role="primary")
        dialog.add_button("Create New", role="secondary")
        dialog.add_button("Cancel", role="secondary")
        
        dialog.exec()
        
        if dialog.clicked_button == "Resume Existing":
            # Show list to resume
            items = [d.title for d in active_drafts]
            list_dialog = ModernListDialog("Select Draft", items, self.parent())
            
            if list_dialog.exec() == ModernListDialog.DialogCode.Accepted and list_dialog.selected_item:
                item = list_dialog.selected_item
                # Find matching draft
                selected_draft = next((d for d in active_drafts if d.title == item), None)
                if selected_draft:
                    self.ctx.draft_manager.set_active_draft(selected_draft.draft_id)
                    self.ctx.store.active_interview_mode = mode_id
                    self.ctx.navigation_controller.push("interview_config")
                    
        elif dialog.clicked_button == "Create New":
            new_draft = self.ctx.draft_manager.create_draft(mode_id, mode_title)
            self.ctx.draft_manager.set_active_draft(new_draft.draft_id)
            self.ctx.store.active_interview_mode = mode_id
            self.ctx.navigation_controller.push("interview_config")

    def go_to_history(self):
        self.ctx.navigation_controller.push("history")

    def go_to_models(self):
        self.ctx.navigation_controller.push("models")

    def go_to_settings(self):
        self.ctx.navigation_controller.push("settings")

    def go_to_report(self):
        self.ctx.navigation_controller.push("report")
