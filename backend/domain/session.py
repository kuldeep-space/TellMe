from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from backend.domain.provider import ProviderConfiguration
import uuid

@dataclass
class AISession:
    """
    Universal execution context used across the entire application.
    Tracks state, config, and conversation history.
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider_id: str = ""
    model: str = ""
    configuration: Optional[ProviderConfiguration] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    runtime_state: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        
    def clear_history(self):
        self.conversation_history.clear()
