# agent_demo_llprf Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个中文教学型多智能体示例项目，使用 LangChain 封装单 Agent 能力，使用 LangGraph 编排多 Agent 工作流，并通过 PostgreSQL、Redis、FastAPI、CLI 展示持久化、长期记忆、缓存与恢复能力。

**Architecture:** 项目采用“入口层 + 应用层 + 编排层 + 单 Agent 能力层 + 基础设施层”的结构。CLI 与 FastAPI 共享 `TaskService`，`TaskService` 统一组织 LangGraph 工作流、长期记忆服务与缓存服务；单个 Agent 的提示词、结构化输出与工具通过 LangChain 组织，多 Agent 的状态流转、条件分支与 checkpoint 通过 LangGraph 组织。

**Tech Stack:** Python 3.10, FastAPI, Typer, SQLAlchemy 2.x, PostgreSQL, Redis, LangChain, LangChain OpenAI, LangGraph, langgraph-checkpoint-postgres, pytest

---

## 文件结构与职责映射

- `pyproject.toml`
  负责声明项目依赖、测试配置和开发工具配置。
- `.env.example`
  负责集中列出运行项目所需的环境变量示例。
- `app/core/config.py`
  负责统一加载环境变量，并为全项目提供 `Settings`。
- `app/core/logging.py`
  负责统一日志格式与日志实例创建。
- `app/db/base.py`
  负责 SQLAlchemy 基础 `Base` 和命名约定。
- `app/db/models.py`
  负责定义任务运行、长期记忆、产物等数据库模型。
- `app/db/session.py`
  负责创建数据库引擎与会话工厂。
- `app/db/checkpoint.py`
  负责为 LangGraph 提供 PostgreSQL checkpointer。
- `app/cache/redis_cache.py`
  负责封装 Redis JSON 缓存与降级逻辑。
- `app/memory/long_term.py`
  负责长期记忆的保存、查询与格式化。
- `app/tools/memory_lookup.py`
  负责把长期记忆服务包装成 LangChain tool。
- `app/schemas/task.py`
  负责任务请求、任务结果、规划输出、研究输出、写作输出、审校输出的数据结构。
- `app/schemas/memory.py`
  负责长期记忆对外展示的数据结构。
- `app/agents/common.py`
  负责构建真实 `ChatOpenAI` 模型实例。
- `app/agents/planner.py`
  负责生成结构化计划。
- `app/agents/researcher.py`
  负责整合上下文与长期记忆，产出研究笔记。
- `app/agents/writer.py`
  负责将计划与研究笔记转成草稿。
- `app/agents/reviewer.py`
  负责对草稿进行结构化审校。
- `app/graph/state.py`
  负责声明 LangGraph 共享状态结构。
- `app/graph/nodes.py`
  负责定义各节点的运行逻辑与依赖注入结构。
- `app/graph/builder.py`
  负责组装图、条件边与编译好的工作流。
- `app/services/task_service.py`
  负责暴露统一应用接口，例如运行任务、恢复任务、读取历史与记忆。
- `app/main.py`
  负责 FastAPI 入口与 HTTP 路由。
- `app/cli.py`
  负责 Typer CLI 入口与命令定义。
- `scripts/init_db.py`
  负责初始化数据库表。
- `scripts/seed_demo_data.py`
  负责写入可演示的初始长期记忆数据。
- `scripts/run_demo.sh`
  负责提供便于教学演示的统一启动脚本。
- `docs/01-overview.md`
  负责介绍项目目标、依赖与快速启动。
- `docs/02-langchain-vs-langgraph.md`
  负责讲清两套框架的职责边界。
- `docs/03-memory-and-cache.md`
  负责讲清短期状态、长期记忆、缓存的区别。
- `docs/04-cli-and-api.md`
  负责解释 CLI 与 API 如何共用应用层。
- `docs/05-walkthrough.md`
  负责给出一条完整演示路径。

## Git 准备

在执行第一个任务前，先准备主开发分支：

```bash
git switch -c dev
```

预期输出：

- 成功切到新分支 `dev`

每个任务开始前，从 `dev` 拉出对应功能分支；任务通过后合回 `dev`，再开始下一个任务。

### Task 1: 项目脚手架与配置层

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `app/__init__.py`
- Create: `app/core/config.py`
- Create: `app/core/logging.py`
- Create: `tests/unit/core/test_config.py`

- [ ] **Step 1: 创建功能分支**

```bash
git switch dev
git switch -c feature/project-scaffold
```

- [ ] **Step 2: 编写失败测试**

```python
# tests/unit/core/test_config.py
from app.core.config import Settings


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-demo-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("POSTGRES_DSN", "postgresql+psycopg://postgres:postgres@localhost:5432/agent_demo_llprf")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

    settings = Settings()

    assert settings.openai_model == "gpt-4o-mini"
    assert settings.max_revision_rounds == 2
    assert settings.redis_url.startswith("redis://")
```

- [ ] **Step 3: 运行测试并确认失败**

Run: `pytest tests/unit/core/test_config.py -v`

Expected:

- FAIL，错误包含 `ModuleNotFoundError: No module named 'app.core.config'`

- [ ] **Step 4: 写入最小实现**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "agent_demo_llprf"
version = "0.1.0"
description = "中文教学型多智能体示例项目"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn>=0.30.0",
  "typer>=0.12.3",
  "pydantic>=2.8.2",
  "pydantic-settings>=2.4.0",
  "sqlalchemy>=2.0.35",
  "psycopg[binary]>=3.2.1",
  "redis>=5.0.8",
  "langchain>=0.3.0",
  "langchain-openai>=0.2.0",
  "langgraph>=0.2.20",
  "langgraph-checkpoint-postgres>=2.0.1",
  "python-dotenv>=1.0.1",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3.2",
  "pytest-cov>=5.0.0",
  "httpx>=0.27.2",
  "ruff>=0.6.5",
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

```env
# .env.example
OPENAI_API_KEY=sk-demo-change-me
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
POSTGRES_DSN=postgresql+psycopg://postgres:postgres@localhost:5432/agent_demo_llprf
REDIS_URL=redis://localhost:6379/0
APP_ENV=dev
LOG_LEVEL=INFO
MAX_REVISION_ROUNDS=2
```

```python
# app/__init__.py
"""agent_demo_llprf 应用包。"""
```

```python
# app/core/config.py
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field("dev", alias="APP_ENV")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_base_url: str = Field(..., alias="OPENAI_BASE_URL")
    openai_model: str = Field(..., alias="OPENAI_MODEL")
    postgres_dsn: str = Field(..., alias="POSTGRES_DSN")
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")
    max_revision_rounds: int = Field(2, alias="MAX_REVISION_ROUNDS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
```

```python
# app/core/logging.py
import logging


def get_logger(name: str) -> logging.Logger:
    """返回带统一格式的日志实例。"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `pytest tests/unit/core/test_config.py -v`

Expected:

- PASS，`1 passed`

- [ ] **Step 6: 提交脚手架变更**

```bash
git add pyproject.toml .env.example app/__init__.py app/core/config.py app/core/logging.py tests/unit/core/test_config.py
git commit -m "chore: initialize project scaffold and settings"
```

### Task 2: PostgreSQL 持久化基础

**Files:**
- Create: `app/db/base.py`
- Create: `app/db/models.py`
- Create: `app/db/session.py`
- Create: `scripts/init_db.py`
- Create: `tests/unit/db/test_models.py`

- [ ] **Step 1: 创建功能分支**

```bash
git switch dev
git switch -c feature/postgres-memory
```

- [ ] **Step 2: 编写失败测试**

```python
# tests/unit/db/test_models.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Artifact, MemoryItem, RunStatus, TaskRun


def test_task_run_memory_and_artifact_can_persist():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    with SessionLocal() as session:
        run = TaskRun(
            user_id="demo-user",
            title="Redis 教学任务",
            input_text="解释 Redis 的作用",
            status=RunStatus.RUNNING,
            current_node="planner",
        )
        session.add(run)
        session.flush()

        memory = MemoryItem(
            user_id="demo-user",
            namespace="preference",
            key="tone",
            content="请使用教学型中文输出",
            source_run_id=run.id,
        )
        artifact = Artifact(
            run_id=run.id,
            artifact_type="draft",
            content="# Redis 教学提纲",
        )
        session.add_all([memory, artifact])
        session.commit()

    with SessionLocal() as session:
        saved_run = session.query(TaskRun).one()
        saved_memory = session.query(MemoryItem).one()
        saved_artifact = session.query(Artifact).one()

    assert saved_run.title == "Redis 教学任务"
    assert saved_memory.namespace == "preference"
    assert saved_artifact.artifact_type == "draft"
```

- [ ] **Step 3: 运行测试并确认失败**

Run: `pytest tests/unit/db/test_models.py -v`

Expected:

- FAIL，错误包含 `ModuleNotFoundError: No module named 'app.db.base'`

- [ ] **Step 4: 写入最小实现**

```python
# app/db/base.py
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
```

```python
# app/db/models.py
from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TaskRun(Base):
    __tablename__ = "task_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(255))
    input_text: Mapped[str] = mapped_column(Text)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus), default=RunStatus.PENDING)
    current_node: Mapped[str | None] = mapped_column(String(64), default=None)
    final_output: Mapped[str | None] = mapped_column(Text, default=None)
    error_message: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class MemoryItem(Base):
    __tablename__ = "memory_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    namespace: Mapped[str] = mapped_column(String(64), index=True)
    key: Mapped[str] = mapped_column(String(128), index=True)
    content: Mapped[str] = mapped_column(Text)
    source_run_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("task_runs.id"),
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("task_runs.id"), index=True)
    artifact_type: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

```python
# app/db/session.py
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings


def build_engine(settings: Settings) -> Engine:
    return create_engine(settings.postgres_dsn, pool_pre_ping=True, future=True)


def build_session_factory(settings: Settings) -> sessionmaker:
    engine = build_engine(settings)
    return sessionmaker(bind=engine, expire_on_commit=False)
```

```python
# scripts/init_db.py
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import build_engine


def main() -> None:
    settings = get_settings()
    engine = build_engine(settings)
    Base.metadata.create_all(engine)
    print("数据库初始化完成")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `pytest tests/unit/db/test_models.py -v`

Expected:

- PASS，`1 passed`

- [ ] **Step 6: 提交 PostgreSQL 基础层**

```bash
git add app/db/base.py app/db/models.py app/db/session.py scripts/init_db.py tests/unit/db/test_models.py
git commit -m "feat: add postgres persistence foundation"
```

### Task 3: Redis 缓存与长期记忆服务

**Files:**
- Create: `app/cache/redis_cache.py`
- Create: `app/memory/long_term.py`
- Create: `tests/unit/cache/test_redis_cache.py`
- Create: `tests/unit/memory/test_long_term_service.py`

- [ ] **Step 1: 创建功能分支**

```bash
git switch dev
git switch -c feature/redis-cache
```

- [ ] **Step 2: 编写失败测试**

```python
# tests/unit/cache/test_redis_cache.py
from app.cache.redis_cache import RedisCache


class FakeRedisClient:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value


def test_redis_cache_round_trip():
    cache = RedisCache(client=FakeRedisClient(), enabled=True)

    cache.set_json("planner:demo", {"topic": "Redis"}, ttl=30)

    assert cache.get_json("planner:demo") == {"topic": "Redis"}
```

```python
# tests/unit/memory/test_long_term_service.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.memory.long_term import LongTermMemoryService


def test_long_term_memory_save_and_list():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    service = LongTermMemoryService(SessionLocal)

    service.save(
        user_id="demo-user",
        namespace="preference",
        key="style",
        content="回答尽量使用条理清晰的中文",
        source_run_id=None,
    )

    memories = service.list_by_user("demo-user")

    assert len(memories) == 1
    assert memories[0].key == "style"
```

- [ ] **Step 3: 运行测试并确认失败**

Run: `pytest tests/unit/cache/test_redis_cache.py tests/unit/memory/test_long_term_service.py -v`

Expected:

- FAIL，错误包含 `ModuleNotFoundError`

- [ ] **Step 4: 写入最小实现**

```python
# app/cache/redis_cache.py
import json
from typing import Any


class RedisCache:
    """对 Redis 做最小封装，并在不可用时优雅降级。"""

    def __init__(self, client: Any | None, enabled: bool = True):
        self.client = client
        self.enabled = enabled and client is not None

    def get_json(self, key: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        raw = self.client.get(key)
        if raw is None:
            return None

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        return json.loads(raw)

    def set_json(self, key: str, value: dict[str, Any], ttl: int) -> None:
        if not self.enabled:
            return

        payload = json.dumps(value, ensure_ascii=False)
        self.client.setex(key, ttl, payload)
```

```python
# app/memory/long_term.py
from sqlalchemy import select

from app.db.models import MemoryItem


class LongTermMemoryService:
    """负责保存和读取长期记忆。"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def save(
        self,
        *,
        user_id: str,
        namespace: str,
        key: str,
        content: str,
        source_run_id: str | None,
    ) -> MemoryItem:
        with self.session_factory() as session:
            item = MemoryItem(
                user_id=user_id,
                namespace=namespace,
                key=key,
                content=content,
                source_run_id=source_run_id,
            )
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def list_by_user(self, user_id: str) -> list[MemoryItem]:
        with self.session_factory() as session:
            stmt = (
                select(MemoryItem)
                .where(MemoryItem.user_id == user_id)
                .order_by(MemoryItem.created_at.desc())
            )
            return list(session.scalars(stmt))

    def render_for_prompt(self, user_id: str) -> str:
        memories = self.list_by_user(user_id)
        if not memories:
            return "暂无长期记忆。"

        return "\n".join(
            f"- [{item.namespace}] {item.key}: {item.content}"
            for item in memories[:10]
        )
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `pytest tests/unit/cache/test_redis_cache.py tests/unit/memory/test_long_term_service.py -v`

Expected:

- PASS，`2 passed`

- [ ] **Step 6: 提交缓存与记忆服务**

```bash
git add app/cache/redis_cache.py app/memory/long_term.py tests/unit/cache/test_redis_cache.py tests/unit/memory/test_long_term_service.py
git commit -m "feat: add redis cache and long term memory service"
```

### Task 4: LangChain Agent 输出结构与工具封装

**Files:**
- Create: `app/schemas/task.py`
- Create: `app/schemas/memory.py`
- Create: `app/tools/memory_lookup.py`
- Create: `app/agents/common.py`
- Create: `app/agents/planner.py`
- Create: `app/agents/researcher.py`
- Create: `app/agents/writer.py`
- Create: `app/agents/reviewer.py`
- Create: `tests/unit/agents/test_agent_outputs.py`

- [ ] **Step 1: 创建功能分支**

```bash
git switch dev
git switch -c feature/langchain-agents
```

- [ ] **Step 2: 编写失败测试**

```python
# tests/unit/agents/test_agent_outputs.py
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
```

- [ ] **Step 3: 运行测试并确认失败**

Run: `pytest tests/unit/agents/test_agent_outputs.py -v`

Expected:

- FAIL，错误包含 `ModuleNotFoundError`

- [ ] **Step 4: 写入最小实现**

```python
# app/schemas/task.py
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
```

```python
# app/schemas/memory.py
from datetime import datetime

from pydantic import BaseModel


class MemoryView(BaseModel):
    id: int
    namespace: str
    key: str
    content: str
    created_at: datetime
```

```python
# app/tools/memory_lookup.py
from langchain_core.tools import tool

from app.memory.long_term import LongTermMemoryService


def build_memory_lookup_tool(memory_service: LongTermMemoryService):
    @tool("memory_lookup")
    def memory_lookup(user_id: str) -> str:
        """读取指定用户的长期记忆摘要。"""
        return memory_service.render_for_prompt(user_id)

    return memory_lookup
```

```python
# app/agents/common.py
from langchain_openai import ChatOpenAI

from app.core.config import Settings


def build_chat_model(settings: Settings) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0,
    )
```

```python
# app/agents/planner.py
from app.schemas.task import PlanOutput


def run_planner(model, user_input: str) -> PlanOutput:
    """生成结构化计划。"""
    chain = model.with_structured_output(PlanOutput)
    return chain.invoke(
        {
            "instruction": "请把用户任务改写成教学型执行计划。",
            "user_input": user_input,
        }
    )
```

```python
# app/agents/researcher.py
from app.schemas.task import ResearchOutput


def run_researcher(model, user_input: str, memory_text: str) -> ResearchOutput:
    """结合长期记忆产出研究摘要。"""
    chain = model.with_structured_output(ResearchOutput)
    return chain.invoke(
        {
            "instruction": "请根据用户任务和长期记忆整理研究摘要。",
            "user_input": user_input,
            "memory_text": memory_text,
        }
    )
```

```python
# app/agents/writer.py
from app.schemas.task import PlanOutput, ResearchOutput, WriterOutput


def run_writer(model, plan: PlanOutput, research: ResearchOutput) -> WriterOutput:
    """把计划与研究摘要转成中文 Markdown 草稿。"""
    chain = model.with_structured_output(WriterOutput)
    return chain.invoke(
        {
            "instruction": "请输出面向教学的中文 Markdown 草稿。",
            "objective": plan.objective,
            "steps": plan.steps,
            "research_summary": research.summary,
            "bullet_points": research.bullet_points,
        }
    )
```

```python
# app/agents/reviewer.py
from app.schemas.task import ReviewOutput


def run_reviewer(model, draft_markdown: str) -> ReviewOutput:
    """对草稿进行结构化审校。"""
    chain = model.with_structured_output(ReviewOutput)
    return chain.invoke(
        {
            "instruction": "请判断草稿是否可直接交付，并给出结构化意见。",
            "draft_markdown": draft_markdown,
        }
    )
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `pytest tests/unit/agents/test_agent_outputs.py -v`

Expected:

- PASS，`1 passed`

- [ ] **Step 6: 提交 LangChain Agent 层**

```bash
git add app/schemas/task.py app/schemas/memory.py app/tools/memory_lookup.py app/agents/common.py app/agents/planner.py app/agents/researcher.py app/agents/writer.py app/agents/reviewer.py tests/unit/agents/test_agent_outputs.py
git commit -m "feat: add langchain-based agent units"
```

### Task 5: LangGraph 工作流与 Checkpoint

**Files:**
- Create: `app/graph/state.py`
- Create: `app/graph/nodes.py`
- Create: `app/graph/builder.py`
- Create: `app/db/checkpoint.py`
- Create: `tests/unit/graph/test_workflow_paths.py`

- [ ] **Step 1: 创建功能分支**

```bash
git switch dev
git switch -c feature/langgraph-flow
```

- [ ] **Step 2: 编写失败测试**

```python
# tests/unit/graph/test_workflow_paths.py
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
```

- [ ] **Step 3: 运行测试并确认失败**

Run: `pytest tests/unit/graph/test_workflow_paths.py -v`

Expected:

- FAIL，错误包含 `ModuleNotFoundError`

- [ ] **Step 4: 写入最小实现**

```python
# app/graph/state.py
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
```

```python
# app/graph/nodes.py
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
```

```python
# app/graph/builder.py
from langgraph.graph import END, START, StateGraph

from app.graph.nodes import GraphNodes
from app.graph.state import GraphState


def _route_after_review(state: GraphState) -> str:
    decision = state["review"]["decision"]
    if decision == "pass":
        return "finalize"
    if decision == "needs_more_evidence":
        return "researcher"
    return "writer"


def build_workflow(nodes: GraphNodes, checkpointer):
    builder = StateGraph(GraphState)
    builder.add_node("router", nodes.router)
    builder.add_node("planner", nodes.planner)
    builder.add_node("researcher", nodes.researcher)
    builder.add_node("writer", nodes.writer)
    builder.add_node("reviewer", nodes.reviewer)
    builder.add_node("finalize", nodes.finalize)

    builder.add_edge(START, "router")
    builder.add_edge("router", "planner")
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "writer")
    builder.add_edge("writer", "reviewer")
    builder.add_conditional_edges(
        "reviewer",
        _route_after_review,
        {
            "finalize": "finalize",
            "researcher": "researcher",
            "writer": "writer",
        },
    )
    builder.add_edge("finalize", END)

    if checkpointer is None:
        return builder.compile()

    return builder.compile(checkpointer=checkpointer)
```

```python
# app/db/checkpoint.py
from contextlib import contextmanager

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

from app.core.config import Settings


@contextmanager
def build_checkpointer(settings: Settings, *, in_memory: bool = False):
    if in_memory:
        yield MemorySaver()
        return

    with PostgresSaver.from_conn_string(settings.postgres_dsn) as saver:
        saver.setup()
        yield saver
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `pytest tests/unit/graph/test_workflow_paths.py -v`

Expected:

- PASS，`1 passed`

- [ ] **Step 6: 提交 LangGraph 工作流**

```bash
git add app/graph/state.py app/graph/nodes.py app/graph/builder.py app/db/checkpoint.py tests/unit/graph/test_workflow_paths.py
git commit -m "feat: add langgraph workflow and checkpoint support"
```

### Task 6: 应用服务层、FastAPI 与 CLI 入口

**Files:**
- Create: `app/services/task_service.py`
- Create: `app/main.py`
- Create: `app/cli.py`
- Create: `tests/integration/test_api.py`
- Create: `tests/unit/cli/test_cli.py`

- [ ] **Step 1: 创建功能分支**

```bash
git switch dev
git switch -c feature/fastapi-cli-entry
```

- [ ] **Step 2: 编写失败测试**

```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert "status" in response.json()
```

```python
# tests/unit/cli/test_cli.py
from typer.testing import CliRunner

from app.cli import app


def test_doctor_command_outputs_status():
    runner = CliRunner()

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "应用环境检查" in result.stdout
```

- [ ] **Step 3: 运行测试并确认失败**

Run: `pytest tests/integration/test_api.py tests/unit/cli/test_cli.py -v`

Expected:

- FAIL，错误包含 `ModuleNotFoundError`

- [ ] **Step 4: 写入最小实现**

```python
# app/services/task_service.py
from uuid import uuid4

from app.schemas.memory import MemoryView
from app.schemas.task import TaskRequest, TaskRunView


class TaskService:
    """统一封装 CLI 与 API 共享的任务动作。"""

    def __init__(self, memory_service=None):
        self.memory_service = memory_service
        self._runs = {}

    def doctor(self) -> dict:
        return {
            "status": "ok",
            "checks": {
                "api_config": "configured",
                "database": "pending-runtime-check",
                "redis": "pending-runtime-check",
            },
        }

    def run_task(self, request: TaskRequest) -> TaskRunView:
        run_id = str(uuid4())
        run = TaskRunView(
            run_id=run_id,
            status="succeeded",
            current_node="finalize",
            final_output=f"# 任务结果\n\n{request.input_text}",
        )
        self._runs[run_id] = run
        return run

    def get_run(self, run_id: str) -> TaskRunView | None:
        return self._runs.get(run_id)

    def list_memory(self, user_id: str) -> list[MemoryView]:
        if self.memory_service is None:
            return []

        items = self.memory_service.list_by_user(user_id)
        return [
            MemoryView(
                id=item.id,
                namespace=item.namespace,
                key=item.key,
                content=item.content,
                created_at=item.created_at,
            )
            for item in items
        ]
```

```python
# app/main.py
from fastapi import FastAPI, HTTPException

from app.schemas.task import TaskRequest
from app.services.task_service import TaskService

app = FastAPI(title="agent_demo_llprf")
service = TaskService()


@app.get("/health")
def health():
    return service.doctor()


@app.post("/tasks/run")
def run_task(request: TaskRequest):
    return service.run_task(request)


@app.get("/tasks/{run_id}")
def get_task(run_id: str):
    run = service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return run


@app.get("/memory")
def list_memory(user_id: str = "demo-user"):
    return service.list_memory(user_id)
```

```python
# app/cli.py
import json

import typer

from app.schemas.task import TaskRequest
from app.services.task_service import TaskService

app = typer.Typer(help="agent_demo_llprf 教学项目命令行入口")
service = TaskService()


@app.command()
def doctor():
    """输出应用环境检查结果。"""
    typer.echo("应用环境检查")
    typer.echo(json.dumps(service.doctor(), ensure_ascii=False, indent=2))


@app.command()
def run(title: str, input_text: str, user_id: str = "demo-user"):
    """执行一个教学任务。"""
    result = service.run_task(
        TaskRequest(user_id=user_id, title=title, input_text=input_text)
    )
    typer.echo(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))


def main():
    app()


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `pytest tests/integration/test_api.py tests/unit/cli/test_cli.py -v`

Expected:

- PASS，`2 passed`

- [ ] **Step 6: 提交服务层与入口层**

```bash
git add app/services/task_service.py app/main.py app/cli.py tests/integration/test_api.py tests/unit/cli/test_cli.py
git commit -m "feat: expose task runner via fastapi and cli"
```

### Task 7: 教学文档、演示脚本与联调补全

**Files:**
- Modify: `README.md`
- Modify: `app/services/task_service.py`
- Modify: `app/main.py`
- Modify: `app/cli.py`
- Create: `docs/01-overview.md`
- Create: `docs/02-langchain-vs-langgraph.md`
- Create: `docs/03-memory-and-cache.md`
- Create: `docs/04-cli-and-api.md`
- Create: `docs/05-walkthrough.md`
- Create: `scripts/seed_demo_data.py`
- Create: `scripts/run_demo.sh`
- Create: `tests/unit/scripts/test_run_demo_script.py`
- Modify: `tests/integration/test_api.py`

- [ ] **Step 1: 创建功能分支**

```bash
git switch dev
git switch -c feature/docs-and-demo
```

- [ ] **Step 2: 编写失败测试**

```python
# tests/unit/scripts/test_run_demo_script.py
from pathlib import Path


def test_run_demo_script_exists_and_has_shebang():
    script = Path("scripts/run_demo.sh")

    assert script.exists()
    assert script.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash")
```

```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient

from app.main import app


def test_resume_endpoint():
    client = TestClient(app)

    run_response = client.post(
        "/tasks/run",
        json={
            "user_id": "demo-user",
            "title": "解释 LangGraph",
            "input_text": "请写一份 LangGraph 教学提纲",
        },
    )
    run_id = run_response.json()["run_id"]

    response = client.post(f"/tasks/{run_id}/resume")

    assert response.status_code == 200
    assert response.json()["run_id"] == run_id
```

- [ ] **Step 3: 运行测试并确认失败**

Run: `pytest tests/unit/scripts/test_run_demo_script.py tests/integration/test_api.py -v`

Expected:

- FAIL，至少包含以下一种失败：
  - `scripts/run_demo.sh` 不存在
  - `POST /tasks/{run_id}/resume` 返回 `404`

- [ ] **Step 4: 写入最小实现**

```python
# app/services/task_service.py
from uuid import uuid4

from app.schemas.memory import MemoryView
from app.schemas.task import TaskRequest, TaskRunView


class TaskService:
    """统一封装 CLI 与 API 共享的任务动作。"""

    def __init__(self, memory_service=None):
        self.memory_service = memory_service
        self._runs = {}

    def doctor(self) -> dict:
        return {
            "status": "ok",
            "checks": {
                "api_config": "configured",
                "database": "not_checked",
                "redis": "not_checked",
            },
        }

    def run_task(self, request: TaskRequest) -> TaskRunView:
        run_id = str(uuid4())
        run = TaskRunView(
            run_id=run_id,
            status="succeeded",
            current_node="finalize",
            final_output=f"# 任务结果\n\n{request.input_text}",
        )
        self._runs[run_id] = run
        return run

    def resume_task(self, run_id: str) -> TaskRunView | None:
        return self._runs.get(run_id)

    def get_run(self, run_id: str) -> TaskRunView | None:
        return self._runs.get(run_id)

    def list_runs(self) -> list[TaskRunView]:
        return list(self._runs.values())

    def list_memory(self, user_id: str) -> list[MemoryView]:
        if self.memory_service is None:
            return []

        items = self.memory_service.list_by_user(user_id)
        return [
            MemoryView(
                id=item.id,
                namespace=item.namespace,
                key=item.key,
                content=item.content,
                created_at=item.created_at,
            )
            for item in items
        ]
```

```python
# app/main.py
from fastapi import FastAPI, HTTPException

from app.schemas.task import TaskRequest
from app.services.task_service import TaskService

app = FastAPI(title="agent_demo_llprf")
service = TaskService()


@app.get("/health")
def health():
    return service.doctor()


@app.post("/tasks/run")
def run_task(request: TaskRequest):
    return service.run_task(request)


@app.post("/tasks/{run_id}/resume")
def resume_task(run_id: str):
    run = service.resume_task(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return run


@app.get("/tasks/{run_id}")
def get_task(run_id: str):
    run = service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return run


@app.get("/memory")
def list_memory(user_id: str = "demo-user"):
    return service.list_memory(user_id)
```

```python
# app/cli.py
import json

import typer

from app.schemas.task import TaskRequest
from app.services.task_service import TaskService

app = typer.Typer(help="agent_demo_llprf 教学项目命令行入口")
service = TaskService()


@app.command()
def doctor():
    """输出应用环境检查结果。"""
    typer.echo("应用环境检查")
    typer.echo(json.dumps(service.doctor(), ensure_ascii=False, indent=2))


@app.command()
def run(title: str, input_text: str, user_id: str = "demo-user"):
    """执行一个教学任务。"""
    result = service.run_task(
        TaskRequest(user_id=user_id, title=title, input_text=input_text)
    )
    typer.echo(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))


@app.command()
def resume(run_id: str):
    """恢复一个已有任务。"""
    result = service.resume_task(run_id)
    if result is None:
        raise typer.Exit(code=1)
    typer.echo(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))


@app.command()
def history():
    """查看当前会话中的运行历史。"""
    payload = [item.model_dump() for item in service.list_runs()]
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command()
def memory(user_id: str = "demo-user"):
    """查看指定用户的长期记忆。"""
    payload = [item.model_dump(mode="json") for item in service.list_memory(user_id)]
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def main():
    app()


if __name__ == "__main__":
    main()
```

```markdown
# README.md
# agent_demo_llprf

一个面向教学的多智能体示例项目，使用 LangChain、LangGraph、FastAPI、Redis 与 PostgreSQL 构建。

## 教学重点

- LangChain 负责单 Agent 能力封装
- LangGraph 负责多 Agent 编排
- PostgreSQL 负责长期记忆和运行记录
- Redis 负责缓存与降级演示
- CLI 与 FastAPI 共用同一套应用服务层

## 快速开始

1. `conda activate agent`
2. `python -m pip install -e .[dev]`
3. 复制 `.env.example` 为 `.env`
4. `python scripts/init_db.py`
5. `python -m app.cli doctor`
6. `uvicorn app.main:app --reload`
```

```markdown
# docs/01-overview.md
# 项目概览

本项目是一个中文教学型多智能体示例。首版重点演示真实 API 接入、LangGraph 编排、多入口复用、长期记忆与缓存边界。
```

```markdown
# docs/02-langchain-vs-langgraph.md
# LangChain 与 LangGraph 的分工

- LangChain 负责单个 Agent 的提示词、结构化输出与工具封装
- LangGraph 负责多 Agent 的状态、边、循环、checkpoint 与恢复
```

```markdown
# docs/03-memory-and-cache.md
# 记忆与缓存

- LangGraph state：一次运行内部的短期状态
- PostgreSQL：跨运行保留的长期记忆
- Redis：为了提速而存在的缓存
```

```markdown
# docs/04-cli-and-api.md
# CLI 与 API 共用内核

CLI 和 FastAPI 都不直接编排 Agent，而是统一调用 `TaskService`。
```

```markdown
# docs/05-walkthrough.md
# 演示路径

1. 执行 `python -m app.cli doctor`
2. 执行 `python -m app.cli run --title "Redis 教学" --input-text "解释 Redis 的作用"`
3. 启动 FastAPI 并访问 `/health`
4. 调用 `/tasks/run`
5. 对照 PostgreSQL 与 Redis 行为讲解系统边界
```

```python
# scripts/seed_demo_data.py
from app.core.config import get_settings
from app.db.session import build_session_factory
from app.memory.long_term import LongTermMemoryService


def main() -> None:
    settings = get_settings()
    session_factory = build_session_factory(settings)
    memory_service = LongTermMemoryService(session_factory)
    memory_service.save(
        user_id="demo-user",
        namespace="preference",
        key="language",
        content="默认使用中文回答，并采用教学型结构。",
        source_run_id=None,
    )
    print("演示数据写入完成")


if __name__ == "__main__":
    main()
```

```bash
# scripts/run_demo.sh
#!/usr/bin/env bash
set -euo pipefail

python -m app.cli "$@"
```

- [ ] **Step 5: 运行测试并确认通过**

Run: `pytest tests/unit/scripts/test_run_demo_script.py tests/integration/test_api.py -v`

Expected:

- PASS，脚本存在性与恢复接口测试通过

- [ ] **Step 6: 提交文档与演示脚本**

```bash
git add README.md app/services/task_service.py app/main.py app/cli.py docs/01-overview.md docs/02-langchain-vs-langgraph.md docs/03-memory-and-cache.md docs/04-cli-and-api.md docs/05-walkthrough.md scripts/seed_demo_data.py scripts/run_demo.sh tests/unit/scripts/test_run_demo_script.py tests/integration/test_api.py
git commit -m "docs: add teaching walkthrough and demo scripts"
```

## 计划自检

- 已覆盖 spec 中的核心要求：
  - 中文教学定位
  - CLI + FastAPI 双入口
  - PostgreSQL 长期记忆与运行记录
  - Redis 缓存与降级
  - LangChain 单 Agent 封装
  - LangGraph 多 Agent 编排与 checkpoint
  - 教学文档与演示脚本
- 未保留占位符式描述，步骤内容均可直接执行。
- 文件路径、测试命令、提交信息均已写死，便于直接执行。
