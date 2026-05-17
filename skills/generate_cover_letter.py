from anthropic import Anthropic
from models.resume import ResumeProfile
from models.job_description import JDRequirements
from models.gap_analysis import GapAnalysis
from models.generated_content import CoverLetter
from skills import _call_structured

SYSTEM_PROMPT = """You are an expert cover letter writer. You craft compelling, personalized cover letters.

RULES:
1. Open with a specific, attention-grabbing hook related to the company or role (not "I am writing to apply...")
2. Connect the candidate's specific achievements to the role's key responsibilities
3. Show genuine enthusiasm for the specific company — reference something specific about them
4. Keep it to 3-4 paragraphs, professional but warm in tone
5. End with a confident call to action
6. Only reference achievements and skills actually present in the candidate's profile
"""


def generate_cover_letter(
    client: Anthropic,
    resume_profile: ResumeProfile,
    jd_requirements: JDRequirements,
    gap_analysis: GapAnalysis,
) -> CoverLetter:
    user_prompt = f"""Write a compelling cover letter for this application.

<candidate>
Name: {resume_profile.full_name}
Summary: {resume_profile.summary}
Key Achievements:
{chr(10).join(f'- {a}' for a in resume_profile.raw_achievements[:10])}
Top Skills: {', '.join(resume_profile.skills[:15])}
</candidate>

<target_role>
Position: {jd_requirements.job_title} at {jd_requirements.company_name}
Seniority: {jd_requirements.seniority_level}
Key Responsibilities:
{chr(10).join(f'- {r}' for r in jd_requirements.key_responsibilities)}
</target_role>

<match_context>
Fit Score: {gap_analysis.overall_fit_score}/10
Strong Matches: {', '.join(m.skill for m in gap_analysis.strong_matches[:5])}
Strategy: {gap_analysis.tailoring_strategy}
</match_context>

Write a cover letter that opens with a compelling hook and connects the candidate's real experience to this specific role."""

    return _call_structured(client, SYSTEM_PROMPT, user_prompt, CoverLetter)
