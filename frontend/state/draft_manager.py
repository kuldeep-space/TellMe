import uuid
import json
import dataclasses
from typing import List, Optional
from datetime import datetime
from PySide6.QtCore import QSettings
from frontend.state.draft_model import InterviewDraft

class DraftManager:
    """
    Encapsulates all domain logic and storage access for interview drafts.
    """
    def __init__(self, store):
        self.store = store
        self._settings = QSettings("TellMe", "AppDrafts")
        self._load_drafts()

    def _load_drafts(self):
        try:
            data = self._settings.value("drafts", "[]")
            if isinstance(data, str):
                drafts_data = json.loads(data)
                for d in drafts_data:
                    draft = InterviewDraft(**d)
                    self.store.drafts[draft.draft_id] = draft
                self.store.drafts_changed.emit(self.store.drafts)
        except Exception as e:
            pass

    def _save_drafts(self):
        try:
            drafts_to_save = [d for d in self.store.drafts.values() if d.status == 'archived' or not d.is_empty]
            drafts_data = [dataclasses.asdict(d) for d in drafts_to_save]
            self._settings.setValue("drafts", json.dumps(drafts_data))
        except Exception as e:
            pass

    def create_draft(self, mode_id: str, title: str) -> InterviewDraft:
        draft = InterviewDraft(
            mode_id=mode_id,
            title=title,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        # Store draft and automatically trigger signals
        self.store.add_draft(draft)
        self._save_drafts()
        return draft

    def get_draft(self, draft_id: str) -> Optional[InterviewDraft]:
        return self.store.drafts.get(draft_id)

    def get_active_drafts_for_mode(self, mode_id: str) -> List[InterviewDraft]:
        return [
            d for d in self.store.drafts.values()
            if d.mode_id == mode_id and d.status == 'active'
        ]

    def update_draft(self, draft_id: str):
        draft = self.get_draft(draft_id)
        if draft:
            draft.updated_at = datetime.now().isoformat()
            draft.has_unsaved_changes = True
            self.store.update_draft(draft)
            self._save_drafts()

    def delete_draft(self, draft_id: str):
        self.store.remove_draft(draft_id)
        self._save_drafts()

    def archive_draft(self, draft_id: str):
        draft = self.get_draft(draft_id)
        if draft:
            draft.status = 'archived'
            draft.updated_at = datetime.now().isoformat()
            self.store.update_draft(draft)
            self._save_drafts()

    def set_active_draft(self, draft_id: Optional[str]):
        current_id = self.store.active_draft_id
        if current_id and current_id != draft_id:
            draft = self.get_draft(current_id)
            if draft and draft.is_empty:
                self.delete_draft(current_id)
                
        self.store.active_draft_id = draft_id
