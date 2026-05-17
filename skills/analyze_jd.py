from anthropic import Anthropic
from models.job_description import JDRequirements
from skills import _call_structured

SYSTEM_PROMPT = """You are an expert job description analyzer. Extract structured requirements from job postings.

RULES:
1. Separate required vs preferred skills carefully — look for language like "required", "must have" vs "nice to have", "preferred"
2. Extract industry-specific keywords and terminology that should appear in a tailored resume
3. Infer seniority level from context if not explicitly stated
4. Keep responsibilities action-oriented (start with verbs)
"""


def analyze_jd(client: Anthropic, jd_text: str) -> JDRequirements:
    user_prompt = f"""Analyze the following job description and extract structured requirements.

<job_description>
{jd_text}
</job_description>"""

    return _call_structured(client, SYSTEM_PROMPT, user_prompt, JDRequirements)
