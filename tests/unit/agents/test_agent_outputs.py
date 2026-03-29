from app.agents.planner import run_planner
from app.schemas.task import PlanOutput


class DummyStructuredChain:
    def __init__(self, schema, payload):
        self.schema = schema
        self.payload = payload

    def invoke(self, _):
        return self.schema(**self.payload)


class DummyModel:
    def __init__(self, payload):
        self.payload = payload

    def with_structured_output(self, schema):
        return DummyStructuredChain(schema, self.payload)


def test_planner_returns_structured_plan():
    model = DummyModel(
        {
            "objective": "解释 Redis 在 Agent 系统中的作用",
            "steps": ["定义 Redis 角色", "解释缓存命中", "说明与长期记忆区别"],
            "success_criteria": ["输出中文", "包含教学结构"],
        }
    )

    result = run_planner(model, "解释 Redis 在 Agent 系统中的作用")

    assert isinstance(result, PlanOutput)
    assert result.objective.startswith("解释 Redis")
    assert len(result.steps) == 3
