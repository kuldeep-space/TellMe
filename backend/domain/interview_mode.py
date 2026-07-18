from dataclasses import dataclass, field
from typing import List, Optional, Any, Callable, Dict
from enum import Enum
from datetime import datetime

class FieldType(Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    FILE = "file"
    DROPDOWN = "dropdown"
    NUMBER = "number"

# -- Validators --
class Validator:
    def validate(self, value: Any, form_data: Dict[str, Any]) -> tuple[bool, str]:
        """Returns (is_valid, error_message)"""
        return True, ""

class RequiredValidator(Validator):
    def validate(self, value: Any, form_data: Dict[str, Any]) -> tuple[bool, str]:
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, "This field is required."
        return True, ""

class AtLeastOneValidator(Validator):
    """Ensures at least one of the specified fields in the form has a value."""
    def __init__(self, field_ids: List[str]):
        self.field_ids = field_ids

    def validate(self, value: Any, form_data: Dict[str, Any]) -> tuple[bool, str]:
        for fid in self.field_ids:
            val = form_data.get(fid)
            if val and str(val).strip():
                return True, ""
        return False, f"At least one of these fields must be provided: {', '.join(self.field_ids)}"

# -- Schemas --
@dataclass
class InputField:
    id: str
    type: FieldType
    label: str
    description: str = ""
    help_text: str = ""
    placeholder: str = ""
    required: bool = True
    options: List[str] = field(default_factory=list)
    default_value: Any = None
    validation_rules: List[Validator] = field(default_factory=list)
    visible_if: Optional[Callable[[Dict[str, Any]], bool]] = None
    enabled_if: Optional[Callable[[Dict[str, Any]], bool]] = None

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
    optional_inputs: List[InputField] = field(default_factory=list)
    feature_list: List[str] = field(default_factory=list)
    primary_action_text: str = "Start Interview"
    primary_action_icon: Optional[str] = None
    primary_action_color: Optional[str] = None

@dataclass
class InterviewConfiguration:
    interview_mode: str
    inputs: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

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

# -- Registrations --

# 1. Resume Interview
InterviewRegistry.register(InterviewMode(
    id="resume_interview",
    title="Resume Interview",
    description="Practice an AI interview based on your uploaded resume.",
    category="Standard",
    icon="FileText",
    estimated_duration="30m",
    difficulty_support=True,
    feature_list=[
        "Resume analysis",
        "Experience-based questions",
        "Real interview simulation"
    ],
    primary_action_text="Start Interview",
    required_inputs=[
        InputField(
            id="resume",
            type=FieldType.FILE,
            label="Resume / CV",
            description="Use your saved resume or upload a new one.",
            placeholder="Upload PDF...",
            required=True,
            validation_rules=[RequiredValidator()]
        )
    ],
    optional_inputs=[
        InputField(
            id="job_role",
            type=FieldType.TEXT,
            label="Target Job Role",
            placeholder="e.g. Software Engineer",
            required=False
        ),
        InputField(
            id="experience_years",
            type=FieldType.NUMBER,
            label="Years of Experience",
            required=False,
            default_value=0
        ),
        InputField(
            id="difficulty",
            type=FieldType.DROPDOWN,
            label="Difficulty",
            required=False,
            options=["Easy", "Medium", "Hard"],
            default_value="Medium"
        ),
        InputField(
            id="duration",
            type=FieldType.DROPDOWN,
            label="Interview Duration",
            required=False,
            options=["15 min", "30 min", "45 min", "60 min"],
            default_value="30 min"
        ),
        InputField(
            id="focus_areas",
            type=FieldType.TEXTAREA,
            label="Resume Focus Areas (Optional)",
            placeholder="e.g. Ask deeply about my React projects. Skip my older internships.",
            required=False
        )
    ]
))

# 2. Company Interview
InterviewRegistry.register(InterviewMode(
    id="company_interview",
    title="Company Interview",
    description="Practice an HR-style interview tailored to a specific job description.",
    category="Standard",
    icon="Briefcase",
    estimated_duration="45m",
    difficulty_support=True,
    feature_list=[
        "JD requirement extraction",
        "Role-specific questions",
        "Company-focused prep"
    ],
    primary_action_text="Start Interview",
    required_inputs=[
        InputField(
            id="jd_text",
            type=FieldType.TEXTAREA,
            label="Job Description Text",
            description="Provide either the text OR a PDF.",
            placeholder="Paste job description...",
            required=False,
            validation_rules=[AtLeastOneValidator(["jd_text", "jd_file"])]
        ),
        InputField(
            id="jd_file",
            type=FieldType.FILE,
            label="Job Description PDF",
            description="Provide either a PDF OR the text.",
            placeholder="Upload JD PDF...",
            required=False,
            validation_rules=[AtLeastOneValidator(["jd_text", "jd_file"])]
        )
    ],
    optional_inputs=[
        InputField(
            id="resume",
            type=FieldType.FILE,
            label="Resume / CV",
            description="Optional context for the interview.",
            placeholder="Upload PDF...",
            required=False
        ),
        InputField(
            id="company_name",
            type=FieldType.TEXT,
            label="Company Name",
            placeholder="e.g. Google",
            required=False
        ),
        InputField(
            id="job_role",
            type=FieldType.TEXT,
            label="Job Role",
            placeholder="e.g. Frontend Developer",
            required=False
        ),
        InputField(
            id="difficulty",
            type=FieldType.DROPDOWN,
            label="Difficulty",
            required=False,
            options=["Easy", "Medium", "Hard"],
            default_value="Medium"
        ),
        InputField(
            id="duration",
            type=FieldType.DROPDOWN,
            label="Interview Duration",
            required=False,
            options=["15 min", "30 min", "45 min", "60 min"],
            default_value="30 min"
        ),
        InputField(
            id="interviewer_persona",
            type=FieldType.DROPDOWN,
            label="Interviewer Persona",
            required=False,
            options=["Friendly", "Strict", "Challenging", "Neutral"],
            default_value="Strict"
        ),
        InputField(
            id="focus_areas",
            type=FieldType.TEXTAREA,
            label="Job-Specific Focus Areas (Optional)",
            placeholder="e.g. Focus on System Design for this role. Emphasize leadership principles.",
            required=False
        )
    ]
))

# 3. Custom Interview
InterviewRegistry.register(InterviewMode(
    id="custom_interview",
    title="Custom Interview",
    description="Create a custom interview by selecting topics and difficulty.",
    category="Custom",
    icon="Settings",
    estimated_duration="Flex",
    difficulty_support=True,
    feature_list=[
        "Custom topics & difficulty",
        "Flexible interview flow",
        "Personalized experience"
    ],
    primary_action_text="Start Interview",
    required_inputs=[
        InputField(
            id="topic",
            type=FieldType.TEXT,
            label="Interview Topic",
            description="What would you like to be interviewed on?",
            placeholder="e.g. Backend Development, React, Networking...",
            required=True,
            validation_rules=[RequiredValidator()]
        )
    ],
    optional_inputs=[
        InputField(
            id="resume",
            type=FieldType.FILE,
            label="Resume / CV",
            description="Optional context for the interview.",
            placeholder="Upload PDF...",
            required=False
        ),
        InputField(
            id="industry",
            type=FieldType.TEXT,
            label="Industry / Domain",
            placeholder="e.g. Tech, Finance, Healthcare",
            required=False
        ),
        InputField(
            id="interview_style",
            type=FieldType.DROPDOWN,
            label="Interview Style",
            required=False,
            options=["Technical", "Behavioral", "System Design", "Mixed"],
            default_value="Mixed"
        ),
        InputField(
            id="interviewer_persona",
            type=FieldType.DROPDOWN,
            label="Interviewer Persona",
            required=False,
            options=["Friendly", "Strict", "Challenging", "Neutral"],
            default_value="Friendly"
        ),
        InputField(
            id="difficulty",
            type=FieldType.DROPDOWN,
            label="Difficulty",
            required=False,
            options=["Easy", "Medium", "Hard"],
            default_value="Medium"
        ),
        InputField(
            id="duration",
            type=FieldType.DROPDOWN,
            label="Interview Duration",
            required=False,
            options=["15 min", "30 min", "45 min", "60 min"],
            default_value="30 min"
        ),
        InputField(
            id="focus_areas",
            type=FieldType.TEXTAREA,
            label="Specific Focus Areas or Instructions",
            placeholder="e.g. Focus on microservices and scalability. Avoid basic syntax questions.",
            required=False
        )
    ]
))
