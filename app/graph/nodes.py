"""LangGraph 节点函数签名与装配结构。"""

from dataclasses import dataclass
from typing import Callable

from app.graph.state import GraphState


# 每个节点都接收共享状态，并返回本轮要写回状态中的增量字段。
NodeFn = Callable[[GraphState], dict]


@dataclass
class GraphNodes:
    """把一组节点函数打包成可编排对象。

    这样 `build_workflow()` 不需要关心节点是如何实现的，只需要关心
    它们之间如何连边。
    """

    router: NodeFn
    planner: NodeFn
    researcher: NodeFn
    writer: NodeFn
    reviewer: NodeFn
    finalize: NodeFn
