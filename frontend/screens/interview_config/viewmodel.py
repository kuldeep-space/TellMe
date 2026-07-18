"""
Interview Configuration ViewModel.
"""
from typing import Dict, Any, Tuple, List, Optional
from frontend.core.base_viewmodel import BaseViewModel
from backend.domain.interview_mode import InterviewRegistry, InterviewConfiguration, InterviewMode

class InterviewConfigViewModel(BaseViewModel):
    def __init__(self, ctx, parent=None):
        super().__init__(ctx, parent)
        self.field_widgets = {} # Maps field_id -> FieldWidget
        self.mode: Optional[InterviewMode] = None

    def load_mode(self):
        """Loads the active mode from the store."""
        active_id = str(self.ctx.store.active_interview_mode)
        self.mode = InterviewRegistry.get(active_id)
        
        # Inject saved profile resume if applicable
        if self.mode:
            saved_resume = self.ctx.profile_service.current_profile.resume_path
            if saved_resume:
                all_fields = (self.mode.required_inputs or []) + (self.mode.optional_inputs or [])
                for field in all_fields:
                    if field.id == "resume":
                        field.default_value = saved_resume

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
