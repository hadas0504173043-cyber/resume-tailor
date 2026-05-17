from langgraph.graph import StateGraph, START, END

from workflow.state import WorkflowState
from workflow.nodes import (
    node_analyze_resume,
    node_analyze_jd,
    node_find_gaps,
    node_generate_resume,
    node_validate,
    node_generate_cover_letter,
)
from workflow.edges import route_after_validation


def build_graph():
    builder = StateGraph(WorkflowState)

    # Register nodes
    builder.add_node("analyze_resume", node_analyze_resume)
    builder.add_node("analyze_jd", node_analyze_jd)
    builder.add_node("find_gaps", node_find_gaps)
    builder.add_node("generate_resume", node_generate_resume)
    builder.add_node("validate", node_validate)
    builder.add_node("generate_cover_letter", node_generate_cover_letter)

    # Parallel fan-out from START
    builder.add_edge(START, "analyze_resume")
    builder.add_edge(START, "analyze_jd")

    # Fan-in: both must complete before find_gaps
    builder.add_edge("analyze_resume", "find_gaps")
    builder.add_edge("analyze_jd", "find_gaps")

    # Linear path to validation
    builder.add_edge("find_gaps", "generate_resume")
    builder.add_edge("generate_resume", "validate")

    # Conditional retry edge
    builder.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "generate_resume": "generate_resume",
            "generate_cover_letter": "generate_cover_letter",
        },
    )

    builder.add_edge("generate_cover_letter", END)

    return builder.compile()


# Singleton compiled graph
graph = build_graph()
