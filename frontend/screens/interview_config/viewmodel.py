"""
Interview Configuration ViewModel.
"""
from typing import Dict, Any, Tuple, List, Optional
from frontend.core.base_viewmodel import BaseViewModel
from backend.domain.interview_mode import InterviewRegistry, InterviewConfiguration, InterviewMode
from frontend.state.draft_model import InterviewDraft

class InterviewConfigViewModel(BaseViewModel):
    def __init__(self, ctx, parent=None):
        super().__init__(ctx, parent)
        self.field_widgets = {} # Maps field_id -> FieldWidget
        self.mode: Optional[InterviewMode] = None

    def load_mode(self):
        """Loads the active mode from the active draft session."""
        draft_id = self.ctx.store.active_draft_id
        if not draft_id:
            return
            
        draft = self.ctx.draft_manager.get_draft(draft_id)
        if not draft:
            return
            
        self.mode = InterviewRegistry.get(draft.mode_id)
        if not self.mode:
            return
            
        # Optional: update resume default dynamically if external managed resume changed
        saved_resume = self.ctx.profile_service.current_profile.resume_path
        if saved_resume:
            for field in (self.mode.required_inputs or []) + (self.mode.optional_inputs or []):
                if field.id == "resume":
                    if "resume" not in draft.configuration:
                        draft.configuration["resume"] = saved_resume
                        self.ctx.draft_manager.update_draft(draft_id)

    def hydrate_and_bind(self):
        """Pre-fills widgets from draft state and attaches value-changed listeners."""
        draft_id = self.ctx.store.active_draft_id
        if not draft_id:
            return
            
        draft = self.ctx.draft_manager.get_draft(draft_id)
        if not draft:
            return
            
        # Pre-fill
        for field_id, widget in self.field_widgets.items():
            if field_id in draft.configuration:
                # Assuming widget has a set_value method. We might need to handle specific types.
                # Since factory.py creates widgets, we'll assume they support set_value.
                if hasattr(widget, "set_value"):
                    widget.set_value(draft.configuration[field_id])
            
            # Bind auto-save
            if hasattr(widget, "value_changed"):
                # Pass field_id using default arg binding in lambda
                widget.value_changed.connect(lambda fid=field_id: self._on_field_changed(fid))

    def _on_field_changed(self, field_id: str):
        draft_id = self.ctx.store.active_draft_id
        if not draft_id: return
        
        draft = self.ctx.draft_manager.get_draft(draft_id)
        if draft and field_id in self.field_widgets:
            widget = self.field_widgets[field_id]
            val = widget.get_value()
            draft.configuration[field_id] = val
            
            # Dynamic title updates based on config
            # e.g., if we have 'company' and 'role'
            if draft.mode_id == 'company':
                comp = draft.configuration.get('company', '').strip()
                role = draft.configuration.get('role', '').strip()
                if comp or role:
                    draft.title = f"{comp} {role}".strip()
                else:
                    draft.title = "Company Interview"
            elif draft.mode_id == 'custom':
                focus = draft.configuration.get('focus_area', '').strip()
                if focus:
                    draft.title = focus[:20] + ("..." if len(focus) > 20 else "")
                else:
                    draft.title = "Custom Interview"

            self.ctx.draft_manager.update_draft(draft_id)

    def go_back(self):
        self.ctx.navigation_controller.push("interview_modes")

    def submit(self) -> Tuple[bool, List[str]]:
        """
        Validates all inputs according to the schema.
        Returns (success, list_of_errors).
        If successful, dispatches configuration to the pipeline and navigates.
        """
        if not self.mode:
            return False, ["No interview mode selected."]
            
        form_data: Dict[str, Any] = {}
        
        # 1. Extract values
        for field_id, widget in self.field_widgets.items():
            form_data[field_id] = widget.get_value()
            
        errors = []
        
        # 2. Validate Required Fields
        for field in self.mode.required_inputs:
            val = form_data.get(field.id)
            if field.validation_rules:
                for rule in field.validation_rules:
                    is_valid, msg = rule.validate(val, form_data)
                    if not is_valid:
                        errors.append(f"{field.label}: {msg}")
                        
        # 3. Validate Optional Fields
        for field in self.mode.optional_inputs:
            val = form_data.get(field.id)
            if field.validation_rules:
                for rule in field.validation_rules:
                    is_valid, msg = rule.validate(val, form_data)
                    if not is_valid:
                        errors.append(f"{field.label}: {msg}")
                        
        # 4. Process Submission if valid
        if errors:
            return False, errors
            
        draft_id = self.ctx.store.active_draft_id
        if draft_id:
            self.ctx.draft_manager.archive_draft(draft_id)
            self.ctx.draft_manager.set_active_draft(None)
            
        # Optional: Additional resume storage logic.
        new_resume = form_data.get("resume")
        if new_resume and new_resume != self.ctx.profile_service.current_profile.resume_path:
            self.ctx.profile_service.update_profile(resume_path=new_resume)
            # update payload to the managed path from profile service
            form_data["resume"] = self.ctx.profile_service.current_profile.resume_path
        
        # 5. Build Configuration Payload
        config = InterviewConfiguration(
            interview_mode=self.mode.id,
            inputs=form_data,
            metadata={
                "version": "1.0",
                "client": "TellMe Desktop"
            }
        )
        
        # 6. Dispatch to Pipeline
        # For now, we store the config in the app state and navigate to the interview runner.
        # This replaces the raw `self.ctx.store.active_interview_mode` reliance in the runner.
        setattr(self.ctx.store, "active_interview_config", config)
        self.ctx.navigation_controller.push("interview")
        
        return True, []
