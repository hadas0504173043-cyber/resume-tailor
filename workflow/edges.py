from typing import Literal
from workflow.state import WorkflowState

MAX_RETRIES = 3


def route_after_validation(
    state: WorkflowState,
) -> Literal["generate_resume", "generate_cover_letter"]:
    validation = state.get("validation_result")
    retry_count = state.get("retry_count", 0)

    if validation is None:
        return "generate_cover_letter"

    if validation.is_valid or retry_count >= MAX_RETRIES:
        return "generate_cover_letter"

    return "generate_resume"
