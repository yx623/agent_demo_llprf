"""LangGraph 共享状态定义。

这里描述的是“一次运行内部”的短期状态，不是长期记忆，也不是缓存。
读者理解这一点之后，就更容易区分 graph state、PostgreSQL 和记忆服务。
"""

from typing import TypedDict


class GraphState(TypedDict, total=False):
    """多 Agent 工作流在节点之间传递的状态载体。"""

    user_id: str
    user_input: str
    route: str
    plan: dict
    research: dict
    draft: str
    review: dict[str, object]
    revision_count: int
    status: str
    final_output: str
