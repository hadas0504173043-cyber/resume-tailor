from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: str
    location: str = ""
    responsibilities: list[str]
    achievements: list[str]


class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    graduation_year: str
    gpa: str = ""
    honors: list[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    full_name: str
    contact_info: dict[str, str]  # email, phone, linkedin, github, location, etc.
    summary: str
    skills: list[str]
    experience: list[WorkExperience]
    education: list[Education]
    certifications: list[str] = Field(default_factory=list)
    raw_achievements: list[str] = Field(
        default_factory=list,
        description="Verbatim achievement strings copied from the original resume — used as ground truth for hallucination validation",
    )
