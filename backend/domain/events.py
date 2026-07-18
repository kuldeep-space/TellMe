from dataclasses import dataclass
from typing import Dict, Any, Optional

class StreamEvent:
    """Base class for all structured streaming events."""
    pass

@dataclass
class GenerationStarted(StreamEvent):
    session_id: str
    model: str

@dataclass
class TokenReceived(StreamEvent):
    text: str
    
@dataclass
class ThinkingStarted(StreamEvent):
    pass

@dataclass
class ThinkingFinished(StreamEvent):
    pass

@dataclass
class ToolCallStarted(StreamEvent):
    tool_name: str
    arguments: Dict[str, Any]

@dataclass
class ToolCallFinished(StreamEvent):
    tool_name: str
    result: Any

@dataclass
class GenerationCompleted(StreamEvent):
    finish_reason: str
    usage: Dict[str, int]
    latency: float

@dataclass
class GenerationCancelled(StreamEvent):
    pass

@dataclass
class GenerationFailed(StreamEvent):
    error_message: str
    error_type: str
