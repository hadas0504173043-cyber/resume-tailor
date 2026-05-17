from anthropic import Anthropic
from models.resume import ResumeProfile
from models.generated_content import TailoredResume
from models.validation import ValidationResult
from skills import _call_structured

SYSTEM_PROMPT = """You are a strict resume validation judge. Your job is to detect hallucinations — content in the tailored resume that was NOT present in the original resume.

WHAT CONSTITUTES A HALLUCINATION:
1. Skills or technologies added that don't appear anywhere in the original resume
2. Changed metrics/numbers (e.g., "15%" changed to "25%", team of 5 changed to team of 10)
3. New employers or companies not in the original
4. New certifications or educational credentials
5. New job titles (title changes, even small ones)
6. Invented tools, platforms, or products

WHAT IS ACCEPTABLE:
1. Reordering of bullet points
2. Rephrasing with job description keywords (as long as meaning is preserved)
3. Adjusted professional summary
4. Emphasis on different aspects of real experience

Be thorough but fair. Only flag actual hallucinations, not stylistic changes.
"""


def validate_content(
    client: Anthropic,
    resume_profile: ResumeProfile,
    tailored_resume: TailoredResume,
    original_resume_text: str,
) -> ValidationResult:
    ground_truth = f"""Original Skills: {', '.join(resume_profile.skills)}
Original Companies: {', '.join(exp.company for exp in resume_profile.experience)}
Original Job Titles: {', '.join(exp.title for exp in resume_profile.experience)}
Original Certifications: {', '.join(resume_profile.certifications)}
Verbatim Achievements (ground truth):
{chr(10).join(f'- {a}' for a in resume_profile.raw_achievements)}"""

    user_prompt = f"""Validate the tailored resume against the original for hallucinations.

<original_resume_text>
{original_resume_text}
</original_resume_text>

<ground_truth>
{ground_truth}
</ground_truth>

<tailored_resume>
{tailored_resume.resume_text}
</tailored_resume>

Check carefully for:
1. Any skill or technology in the tailored resume NOT in the original skills list or resume text
2. Any metric or number that was changed
3. Any company or employer not in the original
4. Any certification or degree not in the original
5. Any job title that differs from the original

Report your findings precisely."""

    return _call_structured(client, SYSTEM_PROMPT, user_prompt, ValidationResult)
