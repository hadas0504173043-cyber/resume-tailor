from anthropic import Anthropic
from models.resume import ResumeProfile
from models.job_description import JDRequirements
from models.gap_analysis import GapAnalysis
from skills import _call_structured

SYSTEM_PROMPT = """You are an expert career coach and resume strategist. Analyze the match between a candidate's profile and a job description.

RULES:
1. Be specific about WHERE in the resume each skill match appears (which company, which project)
2. Partial matches are skills the candidate has experience with but at a lower level or in a different context
3. The fit score (1-10) should reflect honest assessment: 7+ means strong candidate, 4-6 means possible with good tailoring, <4 means weak match
4. The tailoring strategy should be actionable and specific
"""


def find_gaps(
    client: Anthropic,
    resume_profile: ResumeProfile,
    jd_requirements: JDRequirements,
) -> GapAnalysis:
    user_prompt = f"""Analyze the match between this candidate and job opportunity.

<candidate_profile>
Name: {resume_profile.full_name}
Skills: {', '.join(resume_profile.skills)}
Experience:
{chr(10).join(f'- {exp.title} at {exp.company} ({exp.start_date} - {exp.end_date})' for exp in resume_profile.experience)}
Key Achievements:
{chr(10).join(f'- {a}' for a in resume_profile.raw_achievements)}
</candidate_profile>

<job_requirements>
Role: {jd_requirements.job_title} at {jd_requirements.company_name}
Seniority: {jd_requirements.seniority_level}
Required Skills: {', '.join(jd_requirements.required_skills)}
Preferred Skills: {', '.join(jd_requirements.preferred_skills)}
Years Experience Required: {jd_requirements.years_experience_required}
Key Responsibilities:
{chr(10).join(f'- {r}' for r in jd_requirements.key_responsibilities)}
</job_requirements>

Provide a thorough gap analysis and tailoring strategy."""

    return _call_structured(client, SYSTEM_PROMPT, user_prompt, GapAnalysis)
