from anthropic import Anthropic
from models.resume import ResumeProfile
from models.job_description import JDRequirements
from models.gap_analysis import GapAnalysis
from models.generated_content import TailoredResume
from skills import _call_structured

SYSTEM_PROMPT = """You are an expert resume writer. You tailor resumes to specific job descriptions.

STRICT HALLUCINATION PREVENTION RULES — violations will cause rejection:
ALLOWED:
  - Reorder bullet points to lead with most relevant achievements
  - Rephrase descriptions using job description keywords (while preserving meaning)
  - Adjust the professional summary to target the specific role
  - Emphasize relevant skills from the candidate's actual skill set
  - Reorganize sections for impact

FORBIDDEN (will be caught by validation):
  - Adding skills the candidate did not list
  - Changing any numbers, percentages, or metrics
  - Adding employers or companies not in the original resume
  - Inventing projects, tools, or technologies
  - Changing job titles or dates
  - Adding certifications or education not present

When in doubt, use the candidate's original words.
"""


def generate_resume(
    client: Anthropic,
    resume_profile: ResumeProfile,
    jd_requirements: JDRequirements,
    gap_analysis: GapAnalysis,
    original_resume_text: str,
    validation_feedback: list[str] | None = None,
) -> TailoredResume:
    feedback_section = ""
    if validation_feedback:
        feedback_section = f"""
<previous_validation_failures>
The previous version of this resume was rejected for the following reasons. You MUST fix all of these:
{chr(10).join(f'- {issue}' for issue in validation_feedback)}
</previous_validation_failures>
"""

    user_prompt = f"""Tailor this resume for the target job. Follow the hallucination prevention rules strictly.

<original_resume>
{original_resume_text}
</original_resume>

<target_job>
Role: {jd_requirements.job_title} at {jd_requirements.company_name}
Required Skills: {', '.join(jd_requirements.required_skills)}
Preferred Skills: {', '.join(jd_requirements.preferred_skills)}
Key Responsibilities:
{chr(10).join(f'- {r}' for r in jd_requirements.key_responsibilities)}
Industry Keywords: {', '.join(jd_requirements.industry_keywords)}
</target_job>

<tailoring_strategy>
Fit Score: {gap_analysis.overall_fit_score}/10
Strategy: {gap_analysis.tailoring_strategy}
Strong Matches to Emphasize: {', '.join(m.skill for m in gap_analysis.strong_matches)}
Gaps to Acknowledge (do NOT fabricate coverage): {', '.join(gap_analysis.gaps)}
</tailoring_strategy>
{feedback_section}
Produce a professionally formatted tailored resume as plain text."""

    return _call_structured(client, SYSTEM_PROMPT, user_prompt, TailoredResume)
