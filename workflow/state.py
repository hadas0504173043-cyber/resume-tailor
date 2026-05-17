from typing import Optional
from typing_extensions import TypedDict
from models.resume import ResumeProfile
from models.job_description import JDRequirements
from models.gap_analysis import GapAnalysis
from models.generated_content import TailoredResume, CoverLetter
from models.validation import ValidationResult


class WorkflowState(TypedDict):
    raw_resume_text: str           # Never mutated — ground truth for validator
    raw_jd_text: str
    resume_profile: Optional[ResumeProfile]
    jd_requirements: Optional[JDRequirements]
    gap_analysis: Optional[GapAnalysis]
    tailored_resume: Optional[TailoredResume]
    cover_letter: Optional[CoverLetter]
    validation_result: Optional[ValidationResult]
    retry_count: int
    validation_feedback: list[str]  # Accumulated issues across retries
    error: Optional[str]
