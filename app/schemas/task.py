from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    user_id: str = Field(default="demo-user")
    title: str
    input_text: str


class PlanOutput(BaseModel):
    objective: str
    steps: list[str]
    success_criteria: list[str]


class ResearchOutput(BaseModel):
    summary: str
    bullet_points: list[str]


class WriterOutput(BaseModel):
    draft_markdown: str


class ReviewOutput(BaseModel):
    decision: str
    comments: list[str]


class TaskRunView(BaseModel):
    run_id: str
    status: str
    current_node: str | None = None
    final_output: str | None = None
