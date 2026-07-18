from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid

@dataclass
class InterviewDraft:
    """
    Represents an active, unsaved interview configuration session.
    """
    draft_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mode_id: str = ""
    title: str = ""
    status: str = "active" # 'active' or 'archived'
    configuration: Dict[str, Any] = field(default_factory=dict)
    scroll_position: int = 0
    created_at: str = ""
    updated_at: str = ""
    has_unsaved_changes: bool = False

    @property
    def is_empty(self) -> bool:
        for k, v in self.configuration.items():
            if k == 'resume':
                continue
            if isinstance(v, str) and v.strip():
                return False
            if v and not isinstance(v, str):
                return False
        return True
