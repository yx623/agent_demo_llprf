import importlib
import sys
from types import ModuleType

import pytest
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import Settings
from app.graph.builder import build_workflow
from app.graph.nodes import GraphNodes
from app.schemas.task import ReviewOutput


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


def test_workflow_research_retry_path_accepts_review_output():
    researcher_calls = {"count": 0}
    reviewer_calls = {"count": 0}

    def researcher(state):
        researcher_calls["count"] += 1
        return {"research": {"summary": f"第 {researcher_calls['count']} 次补充证据"}}

    def reviewer(state):
        reviewer_calls["count"] += 1
        if reviewer_calls["count"] == 1:
            return {
                "review": ReviewOutput(
                    decision="needs_more_evidence",
                    comments=["补充一条可信来源"],
                )
            }
        return {"review": ReviewOutput(decision="pass", comments=["证据足够"])}

    nodes = GraphNodes(
        router=lambda state: {"route": "new"},
        planner=lambda state: {"plan": {"objective": "解释 Redis"}},
        researcher=researcher,
        writer=lambda state: {"draft": f"# Redis 教学稿\n\n{state['research']['summary']}"},
        reviewer=reviewer,
        finalize=lambda state: {"final_output": state["draft"], "status": "succeeded"},
    )

    workflow = build_workflow(nodes, checkpointer=None, max_revision_rounds=2)
    result = workflow.invoke({"user_input": "解释 Redis", "revision_count": 0})

    assert result["status"] == "succeeded"
    assert result["final_output"].startswith("# Redis 教学稿")
    assert researcher_calls["count"] == 2
    assert result["revision_count"] == 1
    assert isinstance(result["review"], dict)
    assert result["review"]["decision"] == "pass"


def test_workflow_stops_after_revision_limit():
    writer_calls = {"count": 0}

    def writer(state):
        writer_calls["count"] += 1
        return {"draft": f"# 第 {writer_calls['count']} 稿"}

    nodes = GraphNodes(
        router=lambda state: {"route": "new"},
        planner=lambda state: {"plan": {"objective": "解释 Redis"}},
        researcher=lambda state: {"research": {"summary": "Redis 负责缓存"}},
        writer=writer,
        reviewer=lambda state: {
            "review": {"decision": "needs_revision", "comments": ["需要继续改写"]}
        },
        finalize=lambda state: {"final_output": state["draft"], "status": "succeeded"},
    )

    workflow = build_workflow(nodes, checkpointer=None, max_revision_rounds=1)
    result = workflow.invoke({"user_input": "解释 Redis", "revision_count": 0})

    assert result["status"] == "failed"
    assert result["revision_count"] == 1
    assert writer_calls["count"] == 2


def test_workflow_raises_on_invalid_review_decision():
    nodes = GraphNodes(
        router=lambda state: {"route": "new"},
        planner=lambda state: {"plan": {"objective": "解释 Redis"}},
        researcher=lambda state: {"research": {"summary": "Redis 负责缓存"}},
        writer=lambda state: {"draft": "# Redis 教学稿"},
        reviewer=lambda state: {
            "review": {"decision": "approve", "comments": ["错误的决策值"]}
        },
        finalize=lambda state: {"final_output": state["draft"], "status": "succeeded"},
    )

    workflow = build_workflow(nodes, checkpointer=None, max_revision_rounds=1)

    with pytest.raises(ValueError, match="非法 review decision"):
        workflow.invoke({"user_input": "解释 Redis", "revision_count": 0})


def test_build_checkpointer_in_memory_without_postgres_extra():
    sys.modules.pop("app.db.checkpoint", None)

    checkpoint_module = importlib.import_module("app.db.checkpoint")
    settings = Settings.model_construct(postgres_dsn="postgresql+psycopg://user:pass@localhost/db")

    with checkpoint_module.build_checkpointer(settings, in_memory=True) as saver:
        assert isinstance(saver, MemorySaver)


def test_build_checkpointer_normalizes_sqlalchemy_postgres_dsn(monkeypatch):
    sys.modules.pop("app.db.checkpoint", None)
    checkpoint_module = importlib.import_module("app.db.checkpoint")
    settings = Settings.model_construct(
        postgres_dsn="postgresql+psycopg://user:pass@localhost:5432/demo_db"
    )
    observed = {}

    class FakePostgresSaver:
        def __init__(self, conn_string):
            self.conn_string = conn_string

        @classmethod
        def from_conn_string(cls, conn_string):
            observed["conn_string"] = conn_string
            return cls(conn_string)

        def __enter__(self):
            observed["entered"] = True
            return self

        def __exit__(self, exc_type, exc, tb):
            observed["exited"] = True
            return False

        def setup(self):
            observed["setup_called"] = True

    fake_module = ModuleType("langgraph.checkpoint.postgres")
    fake_module.PostgresSaver = FakePostgresSaver
    monkeypatch.setitem(sys.modules, "langgraph.checkpoint.postgres", fake_module)

    with checkpoint_module.build_checkpointer(settings) as saver:
        assert saver.conn_string == "postgresql://user:pass@localhost:5432/demo_db"

    assert observed["conn_string"] == "postgresql://user:pass@localhost:5432/demo_db"
    assert observed["setup_called"] is True
    assert observed["entered"] is True
    assert observed["exited"] is True
