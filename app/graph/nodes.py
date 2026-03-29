from dataclasses import dataclass
from typing import Callable

from app.graph.state import GraphState


NodeFn = Callable[[GraphState], dict]


@dataclass
class GraphNodes:
    router: NodeFn
    planner: NodeFn
    researcher: NodeFn
    writer: NodeFn
    reviewer: NodeFn
    finalize: NodeFn
