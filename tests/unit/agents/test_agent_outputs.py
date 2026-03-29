import pytest
from pydantic import ValidationError

from app.agents.common import build_chat_model
from app.agents.planner import run_planner
from app.agents.researcher import run_researcher
from app.agents.reviewer import run_reviewer
from app.agents.writer import run_writer
from app.schemas.task import (
    PlanOutput,
    ResearchOutput,
    ReviewOutput,
    WriterOutput,
)


class DummyStructuredChain:
    def __init__(self, schema, payload):
        self.schema = schema
        self.payload = payload
        self.last_input = None

    def invoke(self, chain_input):
        self.last_input = chain_input
        return self.schema(**self.payload)


class DummyModel:
    def __init__(self, payload):
        self.payload = payload
        self.last_chain = None

    def with_structured_output(self, schema):
        self.last_chain = DummyStructuredChain(schema, self.payload)
        return self.last_chain


class DummySettings:
    def __init__(self, *, openai_model, openai_api_key, openai_base_url):
        self.openai_model = openai_model
        self.openai_api_key = openai_api_key
        self.openai_base_url = openai_base_url


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
    assert isinstance(model.last_chain.last_input, str)
    assert "解释 Redis 在 Agent 系统中的作用" in model.last_chain.last_input


def test_researcher_uses_string_prompt_with_memory_context():
    model = DummyModel(
        {
            "summary": "Redis 可用于缓存短期上下文，也可辅助工具访问。",
            "bullet_points": ["缓存热点结果", "降低重复检索成本"],
        }
    )

    result = run_researcher(
        model,
        "解释 Redis 在 Agent 系统中的作用",
        "用户偏好：回答时强调缓存与记忆的区别。",
    )

    assert isinstance(result, ResearchOutput)
    assert isinstance(model.last_chain.last_input, str)
    assert "解释 Redis 在 Agent 系统中的作用" in model.last_chain.last_input
    assert "用户偏好：回答时强调缓存与记忆的区别。" in model.last_chain.last_input


def test_writer_uses_string_prompt_with_plan_and_research_content():
    model = DummyModel(
        {
            "draft_markdown": "# Redis\n\n- 先解释缓存\n- 再解释长期记忆",
        }
    )

    plan = PlanOutput(
        objective="解释 Redis 在 Agent 系统中的作用",
        steps=["定义 Redis 角色", "解释缓存命中"],
        success_criteria=["输出中文"],
    )
    research = ResearchOutput(
        summary="Redis 适合存放热点状态与检索结果。",
        bullet_points=["缓存低延迟", "不等于长期记忆"],
    )

    result = run_writer(model, plan, research)

    assert isinstance(result, WriterOutput)
    assert isinstance(model.last_chain.last_input, str)
    assert "解释 Redis 在 Agent 系统中的作用" in model.last_chain.last_input
    assert "Redis 适合存放热点状态与检索结果。" in model.last_chain.last_input
    assert "不等于长期记忆" in model.last_chain.last_input


def test_reviewer_uses_string_prompt_with_draft_content():
    model = DummyModel(
        {
            "decision": "needs_revision",
            "comments": ["需要补充长期记忆与缓存的边界。"],
        }
    )

    result = run_reviewer(model, "# Redis\n\n需要说明与长期记忆的关系。")

    assert isinstance(result, ReviewOutput)
    assert isinstance(model.last_chain.last_input, str)
    assert "# Redis" in model.last_chain.last_input
    assert "长期记忆" in model.last_chain.last_input


def test_build_chat_model_requires_all_openai_settings():
    settings = DummySettings(
        openai_model=None,
        openai_api_key="test-key",
        openai_base_url=None,
    )

    with pytest.raises(ValueError, match="OPENAI_MODEL, OPENAI_BASE_URL"):
        build_chat_model(settings)


def test_review_output_rejects_invalid_decision():
    with pytest.raises(ValidationError):
        ReviewOutput(decision="approve", comments=["格式正确"])


def test_review_output_accepts_allowed_decisions():
    result = ReviewOutput(
        decision="needs_more_evidence",
        comments=["需要增加真实案例。"],
    )

    assert result.decision == "needs_more_evidence"
