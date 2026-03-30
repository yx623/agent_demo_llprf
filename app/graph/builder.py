"""构建多 Agent LangGraph 工作流。"""

from typing import Any

from langgraph.graph import END, START, StateGraph

from app.graph.nodes import GraphNodes
from app.graph.state import GraphState
from app.schemas.task import ReviewOutput


ALLOWED_REVIEW_DECISIONS = {"pass", "needs_revision", "needs_more_evidence"}


def _normalize_review(review: dict[str, Any] | ReviewOutput) -> dict[str, Any]:
    """把 reviewer 输出统一转换成可序列化的 dict。

    这样做有两个目的：
    1. graph state 的结构更稳定
    2. 后续 checkpoint 持久化时不依赖 Pydantic 模型的序列化细节
    """
    if isinstance(review, ReviewOutput):
        return review.model_dump()
    if isinstance(review, dict):
        return review
    raise TypeError("review 节点必须返回 dict 或 ReviewOutput")


def _normalize_reviewer_result(result: dict[str, Any]) -> dict[str, Any]:
    """统一 reviewer 节点的返回格式。"""
    normalized = dict(result)
    normalized["review"] = _normalize_review(result["review"])
    return normalized


def _extract_review_decision(review: dict[str, Any]) -> str:
    """提取并校验 review decision。"""
    decision = review["decision"]
    if decision not in ALLOWED_REVIEW_DECISIONS:
        raise ValueError(f"非法 review decision: {decision}")
    return str(decision)


def _prepare_retry(state: GraphState) -> dict:
    """进入重试前统一递增修订次数。"""
    return {"revision_count": state.get("revision_count", 0) + 1}


def _fail_after_revision_limit(state: GraphState) -> dict:
    """超过重试上限后写入失败状态。"""
    return {"status": "failed"}


def _route_after_review(state: GraphState, *, max_revision_rounds: int) -> str:
    """根据 reviewer 决策决定下一跳。

    这里是整个教学工作流最值得细读的函数之一，因为它集中展示了：
    - review 结果如何驱动工作流
    - 何时继续研究
    - 何时继续改写
    - 何时直接终止
    """
    decision = _extract_review_decision(state["review"])
    if decision == "pass":
        return "finalize"
    if state.get("revision_count", 0) >= max_revision_rounds:
        return "fail"
    if decision == "needs_more_evidence":
        return "prepare_research_retry"
    return "prepare_revision_retry"


def build_workflow(nodes: GraphNodes, checkpointer, max_revision_rounds: int = 2):
    """组装完整的 LangGraph 工作流。

    `nodes` 负责提供单节点行为，`build_workflow` 负责定义节点之间的边。
    这正好体现了 LangChain 与 LangGraph 的分工：前者关注节点内部能力，
    后者关注多节点编排。
    """
    builder = StateGraph(GraphState)
    builder.add_node("router", nodes.router)
    builder.add_node("planner", nodes.planner)
    builder.add_node("researcher", nodes.researcher)
    builder.add_node("writer", nodes.writer)
    builder.add_node(
        "reviewer",
        lambda state: _normalize_reviewer_result(nodes.reviewer(state)),
    )
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
            # reviewer 通过后直接进入最终输出。
            "finalize": "finalize",
            # 证据不足时回到 researcher，补材料后再写作。
            "prepare_research_retry": "prepare_research_retry",
            # 内容质量不足时直接回到 writer，复用已有研究结果。
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
