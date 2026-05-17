from pydantic import BaseModel, Field


class JDRequirements(BaseModel):
    job_title: str
    company_name: str
    seniority_level: str
    required_skills: list[str]
    preferred_skills: list[str] = Field(default_factory=list)
    key_responsibilities: list[str]
    industry_keywords: list[str] = Field(default_factory=list)
    years_experience_required: str = ""
