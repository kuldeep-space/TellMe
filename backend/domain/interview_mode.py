from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class InputField:
    id: str
    type: str                # e.g., "file", "text", "dropdown", "number"
    label: str
    placeholder: str
    required: bool = True
    options: List[str] = field(default_factory=list)

@dataclass
class InterviewMode:
    id: str
    title: str
    description: str
    category: str
    icon: str
    estimated_duration: str
    difficulty_support: bool = False
    required_inputs: List[InputField] = field(default_factory=list)

class InterviewRegistry:
    """Central registry for all dynamic interview modes."""
    _modes: dict[str, InterviewMode] = {}

    @classmethod
    def register(cls, mode: InterviewMode):
        cls._modes[mode.id] = mode

    @classmethod
    def get_all(cls) -> List[InterviewMode]:
        return list(cls._modes.values())

    @classmethod
    def get(cls, mode_id: str) -> Optional[InterviewMode]:
        return cls._modes.get(mode_id)

    @classmethod
    def get_by_category(cls) -> dict[str, List[InterviewMode]]:
        grouped = {}
        for mode in cls.get_all():
            grouped.setdefault(mode.category, []).append(mode)
        return grouped

# ── Register Built-in Modes (Simulated for now, would typically be discovered) ──
InterviewRegistry.register(InterviewMode(
    id="swe_behavioral",
    title="Behavioral & Leadership",
    description="Deep dive into past experiences, conflict resolution, and leadership skills.",
    category="Behavioral",
    icon="Users",
    estimated_duration="30m",
    required_inputs=[
        InputField(id="resume", type="file", label="Resume / CV", placeholder="Upload PDF..."),
        InputField(id="role", type="text", label="Target Role", placeholder="e.g., Engineering Manager")
    ]
))

InterviewRegistry.register(InterviewMode(
    id="swe_technical",
    title="Technical & Algorithmic",
    description="Data structures, problem solving, and low-level system understanding.",
    category="Technical",
    icon="Code",
    estimated_duration="45m",
    difficulty_support=True,
    required_inputs=[
        InputField(id="language", type="dropdown", label="Programming Language", placeholder="Select...", options=["Python", "C++", "Rust", "Go", "Java"]),
        InputField(id="resume", type="file", label="Resume (Optional)", placeholder="Upload PDF...", required=False)
    ]
))

InterviewRegistry.register(InterviewMode(
    id="swe_system_design",
    title="System Design",
    description="Architect scalable backends, distributed systems, and data pipelines.",
    category="Technical",
    icon="Server",
    estimated_duration="45m",
    difficulty_support=True,
    required_inputs=[
        InputField(id="target_company", type="text", label="Target Company (Optional)", placeholder="e.g., Netflix", required=False)
    ]
))

InterviewRegistry.register(InterviewMode(
    id="career_history",
    title="Career History",
    description="A comprehensive walkthrough of your resume, identifying strengths and weaknesses.",
    category="Behavioral",
    icon="Briefcase",
    estimated_duration="30m",
    required_inputs=[
        InputField(id="resume", type="file", label="Resume / CV", placeholder="Upload PDF...")
    ]
))
