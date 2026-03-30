# Learning Guide And Comment Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `agent_demo_llprf` 增加一份系统学习指南，并为 `app/` 与 `scripts/` 核心源码补充面向教学的中文注释。

**Architecture:** 本次改动不改变业务行为，重点增强“可学习性”。文档层新增一份总览式学习指南并在 `README` 中建立入口；代码层通过模块说明、类说明、函数说明与少量关键行内注释解释系统边界、数据流与设计原因。

**Tech Stack:** Markdown, Python, FastAPI, Typer, LangChain, LangGraph, SQLAlchemy, pytest

---

### Task 1: 建立学习入口

**Files:**
- Create: `docs/06-study-guide.md`
- Modify: `README.md`

- [ ] **Step 1: 写学习指南草稿**
- [ ] **Step 2: 明确项目结构树、阅读顺序、学习目标与实验顺序**
- [ ] **Step 3: 在 `README.md` 中增加学习指南入口**

### Task 2: 给核心源码补中文注释

**Files:**
- Modify: `app/agents/common.py`
- Modify: `app/agents/planner.py`
- Modify: `app/agents/researcher.py`
- Modify: `app/agents/reviewer.py`
- Modify: `app/agents/writer.py`
- Modify: `app/cache/redis_cache.py`
- Modify: `app/cli.py`
- Modify: `app/core/config.py`
- Modify: `app/core/logging.py`
- Modify: `app/db/base.py`
- Modify: `app/db/checkpoint.py`
- Modify: `app/db/models.py`
- Modify: `app/db/session.py`
- Modify: `app/graph/builder.py`
- Modify: `app/graph/nodes.py`
- Modify: `app/graph/state.py`
- Modify: `app/main.py`
- Modify: `app/memory/long_term.py`
- Modify: `app/schemas/memory.py`
- Modify: `app/schemas/task.py`
- Modify: `app/services/task_service.py`
- Modify: `app/tools/memory_lookup.py`
- Modify: `scripts/init_db.py`
- Modify: `scripts/seed_demo_data.py`
- Modify: `scripts/run_demo.sh`

- [ ] **Step 1: 为每个文件补模块级说明**
- [ ] **Step 2: 为关键类和函数补职责说明**
- [ ] **Step 3: 在复杂分支和关键数据流处补少量行内中文注释**

### Task 3: 验证与提交

**Files:**
- Verify: `tests/`

- [ ] **Step 1: 运行 `pytest tests -v`**
- [ ] **Step 2: 检查工作区状态**
- [ ] **Step 3: 提交文档与注释增强改动**
