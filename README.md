# Resume Tailor

AI-powered resume and cover letter tailoring with hallucination prevention. Paste your resume and a job description — the system produces a tailored resume, cover letter, and a validation report confirming nothing was fabricated.

## What it demonstrates

- **Prompt engineering** — structured extraction, constrained generation, judge-based validation
- **Structured outputs** — Anthropic tool-use JSON mode + Pydantic v2 models throughout
- **LangGraph workflow** — parallel fan-out, fan-in, and a conditional retry loop
- **Hallucination prevention** — 3-layer system: verbatim extraction → generation constraints → LLM judge validation

## Architecture

```
START → analyze_resume ─┐
START → analyze_jd      ─┴→ find_gaps → generate_resume → validate
                                               ↑                │
                                               └─── (retry) ────┤ invalid & retries < 3
                                                                 ↓
                                                   generate_cover_letter → END
```

`analyze_resume` and `analyze_jd` run in parallel. `find_gaps` fans in after both complete. If the validator detects hallucinations, `generate_resume` is retried with accumulated feedback (up to 3 times) before proceeding to `generate_cover_letter`.

## Project structure

```
resume-tailor/
├── app.py                    # Streamlit UI — no business logic
├── requirements.txt
├── .env.example
├── models/
│   ├── resume.py             # ResumeProfile, WorkExperience, Education
│   ├── job_description.py    # JDRequirements
│   ├── gap_analysis.py       # GapAnalysis, SkillMatch
│   ├── generated_content.py  # TailoredResume, CoverLetter
│   └── validation.py         # ValidationResult
├── skills/
│   ├── __init__.py           # _call_structured() shared helper
│   ├── analyze_resume.py
│   ├── analyze_jd.py
│   ├── find_gaps.py
│   ├── generate_resume.py
│   ├── generate_cover_letter.py
│   └── validate_content.py
└── workflow/
    ├── state.py              # WorkflowState TypedDict
    ├── nodes.py              # One function per LangGraph node
    ├── edges.py              # route_after_validation(), MAX_RETRIES = 3
    ├── graph.py              # build_graph() + compiled singleton
    └── runner.py             # run_workflow() — the only public interface
```

## Installation

### Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)

### Setup

```bash
# 1. Clone or download the project
cd resume-tailor

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# Open .env and set:  ANTHROPIC_API_KEY=sk-ant-...

# 5. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Usage

1. Paste your resume (plain text) in the left panel
2. Paste the job description in the right panel
3. Click **Tailor My Resume**
4. Review the five output sections:
   - **Gap Analysis** — fit score, skill matches, and tailoring strategy
   - **Tailored Resume** — copyable text with a "What changed?" expander
   - **Cover Letter** — copyable text
   - **Validation Status** — pass / retried N times / issues list

## Future API migration

`workflow/runner.py` exposes a single function `run_workflow(resume_text, jd_text) -> WorkflowState`. To add a REST API, create `api.py`:

```python
from fastapi import FastAPI
from workflow.runner import run_workflow

app = FastAPI()

@app.post("/tailor")
def tailor(resume_text: str, jd_text: str):
    result = run_workflow(resume_text, jd_text)
    return result
```

The workflow layer needs zero changes.

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude access |
