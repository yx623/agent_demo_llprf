# agent_demo_llprf

一个面向教学的多智能体示例项目，使用 LangChain、LangGraph、FastAPI、Redis 与 PostgreSQL 构建。

这个项目刻意把“单 Agent 能力”和“多 Agent 编排”拆开演示。你可以先从 CLI 跑通最小流程，再通过 FastAPI、PostgreSQL 和 Redis 观察系统如何保存状态、记忆与缓存。

## 教学重点

- LangChain 负责单 Agent 的提示词、结构化输出与工具封装
- LangGraph 负责多 Agent 的状态流转、循环、checkpoint 与恢复
- PostgreSQL 负责长期记忆与运行记录
- Redis 负责缓存命中与降级演示
- CLI 与 FastAPI 统一复用 `TaskService`

## 快速开始

1. `conda activate agent`
2. `python -m pip install -e .[dev]`
3. 复制 `.env.example` 为 `.env`
4. `python scripts/init_db.py`
5. `python scripts/seed_demo_data.py`
6. `python -m app.cli doctor`
7. `python -m app.cli run "Redis 教学" "解释 Redis 的作用"`
8. `uvicorn app.main:app --reload`

## 教学阅读顺序

1. `docs/01-overview.md`
2. `docs/02-langchain-vs-langgraph.md`
3. `docs/03-memory-and-cache.md`
4. `docs/04-cli-and-api.md`
5. `docs/05-walkthrough.md`

## 常用演示命令

- 健康检查：`python -m app.cli doctor`
- 发起任务：`python -m app.cli run "LangGraph 教学" "请写一份 LangGraph 教学提纲"`
- 查看历史：`python -m app.cli history`
- 查看记忆：`python -m app.cli memory`
- 启动演示脚本：`bash scripts/run_demo.sh doctor`

## 核心设计文档

- `docs/superpowers/specs/2026-03-29-agent-demo-llprf-design.md`
- `docs/superpowers/plans/2026-03-29-agent-demo-llprf.md`
