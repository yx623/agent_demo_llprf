from langgraph.graph import END, START, StateGraph

from app.graph.nodes import GraphNodes
from app.graph.state import GraphState


def _route_after_review(state: GraphState) -> str:
    decision = state["review"]["decision"]
    if decision == "pass":
        return "finalize"
    if decision == "needs_more_evidence":
        return "researcher"
    return "writer"


def build_workflow(nodes: GraphNodes, checkpointer):
    builder = StateGraph(GraphState)
    builder.add_node("router", nodes.router)
    builder.add_node("planner", nodes.planner)
    builder.add_node("researcher", nodes.researcher)
    builder.add_node("writer", nodes.writer)
    builder.add_node("reviewer", nodes.reviewer)
    builder.add_node("finalize", nodes.finalize)

    builder.add_edge(START, "router")
    builder.add_edge("router", "planner")
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "writer")
    builder.add_edge("writer", "reviewer")
    builder.add_conditional_edges(
        "reviewer",
        _route_after_review,
        {
            "finalize": "finalize",
            "researcher": "researcher",
            "writer": "writer",
        },
    )
    builder.add_edge("finalize", END)

    if checkpointer is None:
        return builder.compile()

    return builder.compile(checkpointer=checkpointer)
