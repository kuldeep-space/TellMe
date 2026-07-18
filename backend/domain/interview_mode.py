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
    feature_list: List[str] = field(default_factory=list)
    button_text: str = "Let's Start →"

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

# ── Register Built-in Modes ──
InterviewRegistry.register(InterviewMode(
    id="resume_interview",
    title="Resume Interview",
    description="Practice an AI interview based on your uploaded resume.",
    category="Standard",
    icon="FileText",
    estimated_duration="30m",
    required_inputs=[
        InputField(id="resume", type="file", label="Resume / CV", placeholder="Upload PDF...")
    ],
    feature_list=[
        "Resume analysis",
        "Experience-based questions",
        "Real interview simulation"
    ]
))

InterviewRegistry.register(InterviewMode(
    id="company_interview",
    title="Company Interview",
    description="Practice an HR-style interview tailored to a specific job description.",
    category="Standard",
    icon="Briefcase",
    estimated_duration="45m",
    required_inputs=[
        InputField(id="job_description", type="text", label="Job Description", placeholder="Paste job description...")
    ],
    feature_list=[
        "JD requirement extraction",
        "Role-specific questions",
        "Company-focused prep"
    ]
))

InterviewRegistry.register(InterviewMode(
    id="custom_interview",
    title="Custom Interview",
    description="Create a custom interview by selecting topics and difficulty.",
    category="Custom",
    icon="Settings",
    estimated_duration="Flex",
    difficulty_support=True,
    required_inputs=[
        InputField(id="topics", type="text", label="Topics", placeholder="e.g., Python, System Design")
    ],
    feature_list=[
        "Custom topics & difficulty",
        "Flexible interview flow",
        "Personalized experience"
    ]
))
