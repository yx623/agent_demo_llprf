from typing import TypedDict


class GraphState(TypedDict, total=False):
    user_id: str
    user_input: str
    route: str
    plan: dict
    research: dict
    draft: str
    review: dict
    revision_count: int
    status: str
    final_output: str
