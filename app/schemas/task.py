"""任务相关的输入输出模型。"""

from typing import Literal

from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    """统一的任务请求对象。"""

    user_id: str = Field(default="demo-user")
    title: str
    input_text: str


class PlanOutput(BaseModel):
    """planner 节点的结构化输出。"""

    objective: str
    steps: list[str]
    success_criteria: list[str]


class ResearchOutput(BaseModel):
    """researcher 节点的结构化输出。"""

    summary: str
    bullet_points: list[str]


class WriterOutput(BaseModel):
    """writer 节点的结构化输出。"""

    draft_markdown: str


class ReviewOutput(BaseModel):
    """reviewer 节点的结构化输出。"""

    decision: Literal["pass", "needs_revision", "needs_more_evidence"]
    comments: list[str]


class TaskRunView(BaseModel):
    """对 CLI 和 API 暴露的任务运行视图。"""

    run_id: str
    status: str
    current_node: str | None = None
    final_output: str | None = None
