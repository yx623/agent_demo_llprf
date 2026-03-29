from app.graph.builder import build_workflow
from app.graph.nodes import GraphNodes


def test_workflow_pass_path():
    nodes = GraphNodes(
        router=lambda state: {"route": "new"},
        planner=lambda state: {"plan": {"objective": "解释 Redis"}},
        researcher=lambda state: {"research": {"summary": "Redis 负责缓存"}},
        writer=lambda state: {"draft": "# Redis 教学稿"},
        reviewer=lambda state: {"review": {"decision": "pass", "comments": ["结构完整"]}},
        finalize=lambda state: {"final_output": state["draft"], "status": "succeeded"},
    )

    workflow = build_workflow(nodes, checkpointer=None)
    result = workflow.invoke({"user_input": "解释 Redis", "revision_count": 0})

    assert result["status"] == "succeeded"
    assert result["final_output"] == "# Redis 教学稿"
