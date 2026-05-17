from typing import Literal
from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    is_valid: bool
    issues: list[str] = Field(default_factory=list)
    hallucinated_skills: list[str] = Field(default_factory=list)
    hallucinated_metrics: list[str] = Field(default_factory=list)
    hallucinated_companies: list[str] = Field(default_factory=list)
    severity: Literal["none", "minor", "major"] = "none"
