from langgraph.graph import END, START, StateGraph

from app.graph.nodes import GraphNodes
from app.graph.state import GraphState


def _extract_review_decision(review: object) -> str:
    if isinstance(review, dict):
        return review["decision"]
    return review.decision


def _prepare_retry(state: GraphState) -> dict:
    return {"revision_count": state.get("revision_count", 0) + 1}


def _fail_after_revision_limit(state: GraphState) -> dict:
    return {"status": "failed"}


def _route_after_review(state: GraphState, *, max_revision_rounds: int) -> str:
    decision = _extract_review_decision(state["review"])
    if decision == "pass":
        return "finalize"
    if state.get("revision_count", 0) >= max_revision_rounds:
        return "fail"
    if decision == "needs_more_evidence":
        return "prepare_research_retry"
    return "prepare_revision_retry"


def build_workflow(nodes: GraphNodes, checkpointer, max_revision_rounds: int = 2):
    builder = StateGraph(GraphState)
    builder.add_node("router", nodes.router)
    builder.add_node("planner", nodes.planner)
    builder.add_node("researcher", nodes.researcher)
    builder.add_node("writer", nodes.writer)
    builder.add_node("reviewer", nodes.reviewer)
    builder.add_node("finalize", nodes.finalize)
    builder.add_node("prepare_research_retry", _prepare_retry)
    builder.add_node("prepare_revision_retry", _prepare_retry)
    builder.add_node("fail", _fail_after_revision_limit)

    builder.add_edge(START, "router")
    builder.add_edge("router", "planner")
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "writer")
    builder.add_edge("writer", "reviewer")
    builder.add_conditional_edges(
        "reviewer",
        lambda state: _route_after_review(
            state,
            max_revision_rounds=max_revision_rounds,
        ),
        {
            "finalize": "finalize",
            "prepare_research_retry": "prepare_research_retry",
            "prepare_revision_retry": "prepare_revision_retry",
            "fail": "fail",
        },
    )
    builder.add_edge("prepare_research_retry", "researcher")
    builder.add_edge("prepare_revision_retry", "writer")
    builder.add_edge("finalize", END)
    builder.add_edge("fail", END)

    if checkpointer is None:
        return builder.compile()

    return builder.compile(checkpointer=checkpointer)
