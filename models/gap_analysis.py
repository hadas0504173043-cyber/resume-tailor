from pydantic import BaseModel, Field


class SkillMatch(BaseModel):
    skill: str
    evidence: str  # Where in the resume this skill appears


class GapAnalysis(BaseModel):
    strong_matches: list[SkillMatch]
    partial_matches: list[SkillMatch]
    gaps: list[str]  # Required skills not found in resume
    preferred_present: list[str]  # Preferred skills candidate has
    preferred_absent: list[str]  # Preferred skills candidate lacks
    overall_fit_score: int = Field(ge=1, le=10)
    tailoring_strategy: str  # Narrative explanation of how to best tailor the resume
