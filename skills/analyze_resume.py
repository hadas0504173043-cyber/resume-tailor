from anthropic import Anthropic
from models.resume import ResumeProfile
from skills import _call_structured

SYSTEM_PROMPT = """You are an expert resume parser. Your job is to extract structured information from resumes accurately.

CRITICAL RULES:
1. Copy metrics and achievements EXACTLY as written — do not paraphrase numbers or percentages
2. Preserve verbatim achievement strings in raw_achievements (e.g., "Increased revenue by 47%", "Led team of 12 engineers")
3. Do not infer or add information not present in the resume
4. Extract ALL skills mentioned anywhere in the document
5. If a field is not present, use an empty string or empty list
"""


def analyze_resume(client: Anthropic, resume_text: str) -> ResumeProfile:
    user_prompt = f"""Parse the following resume into structured data.

For raw_achievements, copy every quantified achievement and key accomplishment verbatim from the resume text.
These will be used later to detect hallucinations, so accuracy is critical.

<resume>
{resume_text}
</resume>"""

    return _call_structured(client, SYSTEM_PROMPT, user_prompt, ResumeProfile)
