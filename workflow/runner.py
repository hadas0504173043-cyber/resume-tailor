import time
from logger import get_logger
from workflow.state import WorkflowState
from workflow.graph import graph

log = get_logger("runner")


def run_workflow(resume_text: str, jd_text: str) -> WorkflowState:
    """Public interface for the resume tailoring workflow.

    This is the only import that app.py (or a future API) needs.
    Returns the final WorkflowState with all generated content.
    """
    log.info("=" * 60)
    log.info("workflow started")
    log.info(f"  resume: {len(resume_text)} chars")
    log.info(f"  job description: {len(jd_text)} chars")

    initial_state: WorkflowState = {
        "raw_resume_text": resume_text,
        "raw_jd_text": jd_text,
        "resume_profile": None,
        "jd_requirements": None,
        "gap_analysis": None,
        "tailored_resume": None,
        "cover_letter": None,
        "validation_result": None,
        "retry_count": 0,
        "validation_feedback": [],
        "error": None,
    }

    t0 = time.time()
    result = graph.invoke(initial_state)
    elapsed = time.time() - t0

    if result.get("error"):
        log.error(f"workflow finished with error in {elapsed:.1f}s: {result['error']}")
    else:
        retries = result.get("retry_count", 0)
        valid = result.get("validation_result")
        log.info(
            f"workflow completed in {elapsed:.1f}s — "
            f"retries={retries}, "
            f"validation={'PASS' if valid and valid.is_valid else 'FAIL'}"
        )
    log.info("=" * 60)

    return result
