import os
from anthropic import Anthropic
from dotenv import load_dotenv

from logger import get_logger
from workflow.state import WorkflowState
from skills.analyze_resume import analyze_resume
from skills.analyze_jd import analyze_jd
from skills.find_gaps import find_gaps
from skills.generate_resume import generate_resume
from skills.generate_cover_letter import generate_cover_letter
from skills.validate_content import validate_content

load_dotenv()

log = get_logger("nodes")


def _get_client() -> Anthropic:
    return Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def node_analyze_resume(state: WorkflowState) -> dict:
    log.info("→ analyze_resume: starting")
    try:
        client = _get_client()
        profile = analyze_resume(client, state["raw_resume_text"])
        log.info(f"✓ analyze_resume: parsed '{profile.full_name}', {len(profile.skills)} skills, {len(profile.experience)} roles, {len(profile.raw_achievements)} raw achievements")
        return {"resume_profile": profile}
    except Exception as e:
        log.error(f"✗ analyze_resume failed: {e}")
        return {"error": f"Resume analysis failed: {e}"}


def node_analyze_jd(state: WorkflowState) -> dict:
    log.info("→ analyze_jd: starting")
    try:
        client = _get_client()
        requirements = analyze_jd(client, state["raw_jd_text"])
        log.info(f"✓ analyze_jd: parsed '{requirements.job_title}' at '{requirements.company_name}', {len(requirements.required_skills)} required skills")
        return {"jd_requirements": requirements}
    except Exception as e:
        log.error(f"✗ analyze_jd failed: {e}")
        return {"error": f"Job description analysis failed: {e}"}


def node_find_gaps(state: WorkflowState) -> dict:
    if state.get("error"):
        log.warning("find_gaps: skipped due to upstream error")
        return {}
    log.info("→ find_gaps: starting")
    try:
        client = _get_client()
        analysis = find_gaps(client, state["resume_profile"], state["jd_requirements"])
        log.info(
            f"✓ find_gaps: fit score {analysis.overall_fit_score}/10, "
            f"{len(analysis.strong_matches)} strong matches, "
            f"{len(analysis.gaps)} gaps"
        )
        return {"gap_analysis": analysis}
    except Exception as e:
        log.error(f"✗ find_gaps failed: {e}")
        return {"error": f"Gap analysis failed: {e}"}


def node_generate_resume(state: WorkflowState) -> dict:
    if state.get("error"):
        log.warning("generate_resume: skipped due to upstream error")
        return {}
    retry = state.get("retry_count", 0)
    feedback = state.get("validation_feedback", [])
    log.info(f"→ generate_resume: starting (attempt {retry + 1}, {len(feedback)} feedback items)")
    if feedback:
        log.debug(f"  feedback injected: {feedback}")
    try:
        client = _get_client()
        tailored = generate_resume(
            client,
            state["resume_profile"],
            state["jd_requirements"],
            state["gap_analysis"],
            state["raw_resume_text"],
            feedback,
        )
        log.info(f"✓ generate_resume: {len(tailored.key_changes_made)} changes made, {len(tailored.resume_text)} chars")
        return {"tailored_resume": tailored}
    except Exception as e:
        log.error(f"✗ generate_resume failed: {e}")
        return {"error": f"Resume generation failed: {e}"}


def node_validate(state: WorkflowState) -> dict:
    if state.get("error"):
        log.warning("validate: skipped due to upstream error")
        return {}
    log.info("→ validate: starting hallucination check")
    try:
        client = _get_client()
        result = validate_content(
            client,
            state["resume_profile"],
            state["tailored_resume"],
            state["raw_resume_text"],
        )

        existing_feedback = list(state.get("validation_feedback", []))
        if not result.is_valid:
            existing_feedback.extend(result.issues)

        new_retry_count = state.get("retry_count", 0)
        if not result.is_valid:
            new_retry_count += 1

        if result.is_valid:
            log.info(f"✓ validate: PASSED (severity={result.severity})")
        else:
            log.warning(
                f"✗ validate: FAILED (severity={result.severity}, retry_count now={new_retry_count})\n"
                + "\n".join(f"  - {i}" for i in result.issues)
            )
            if result.hallucinated_skills:
                log.warning(f"  hallucinated skills: {result.hallucinated_skills}")
            if result.hallucinated_metrics:
                log.warning(f"  changed metrics: {result.hallucinated_metrics}")
            if result.hallucinated_companies:
                log.warning(f"  fabricated companies: {result.hallucinated_companies}")

        return {
            "validation_result": result,
            "validation_feedback": existing_feedback,
            "retry_count": new_retry_count,
        }
    except Exception as e:
        log.error(f"✗ validate failed: {e}")
        return {"error": f"Validation failed: {e}"}


def node_generate_cover_letter(state: WorkflowState) -> dict:
    if state.get("error"):
        log.warning("generate_cover_letter: skipped due to upstream error")
        return {}
    log.info("→ generate_cover_letter: starting")
    try:
        client = _get_client()
        letter = generate_cover_letter(
            client,
            state["resume_profile"],
            state["jd_requirements"],
            state["gap_analysis"],
        )
        log.info(f"✓ generate_cover_letter: {len(letter.cover_letter_text)} chars")
        return {"cover_letter": letter}
    except Exception as e:
        log.error(f"✗ generate_cover_letter failed: {e}")
        return {"error": f"Cover letter generation failed: {e}"}
