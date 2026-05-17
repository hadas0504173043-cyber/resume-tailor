from pydantic import BaseModel


class TailoredResume(BaseModel):
    resume_text: str  # Full formatted resume as plain text
    key_changes_made: list[str]  # Human-readable list of what was changed
    skills_emphasized: list[str]  # Skills that were highlighted for this role


class CoverLetter(BaseModel):
    cover_letter_text: str  # Full cover letter as plain text
    opening_hook: str  # The opening hook sentence extracted from the letter
