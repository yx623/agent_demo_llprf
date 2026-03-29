---
title: 理解 agent_demo_llprf 的教学结构
description: 从项目分层、入口和存储边界三个角度快速理解整个示例。
nav_title: 项目概览
---

这个仓库不是为了展示“最强 Agent”，而是为了把多智能体系统里最常见的几个部件拆开讲清楚。你可以在一个很小的代码库里同时看到 LangChain、LangGraph、FastAPI、CLI、PostgreSQL 和 Redis 各自负责什么。

阅读时最容易混乱的地方，是把“单 Agent 的能力”和“多 Agent 的调度”混成一个层。这个项目把它们拆在不同目录里，并通过 `TaskService` 把入口层和编排层连接起来。

## Example

我们把这个项目当成一个“教学稿生成器”来看。它接收一个主题，经过规划、研究、写作和审查后，返回一份中文教学输出。

建议先打开 `app/agents/`、`app/graph/`、`app/services/` 这三个目录，再对照本文往下看。

### Step 1: 先分清入口层和能力层

最外层入口只有两个：CLI 和 FastAPI。

- `app/cli.py` 负责命令行交互。
- `app/main.py` 负责 HTTP 路由。
- `app/services/task_service.py` 负责把两个入口统一到一套任务动作上。

如果没有这一层，CLI 和 API 很容易各写一套逻辑。那样一旦你修改任务执行流程，两边就会一起漂移。现在两个入口都只调用 `TaskService`，所以演示口径是统一的。

可观察的验证方式是分别运行：

- `python -m app.cli doctor`
- `uvicorn app.main:app --reload`

你会看到两个入口暴露的是同一组能力，而不是两套实现。

### Step 2: 再区分 LangChain 和 LangGraph

`app/agents/` 放的是单个 Agent 的能力单元，例如 planner、researcher、writer、reviewer。它们的重点是提示词、结构化输出和工具调用。

`app/graph/` 放的是多 Agent 工作流。这里不关心某个 Agent 用了什么 prompt，而是关心状态怎么流动、什么时候回环、什么时候终止。

如果把这两层混在一起，测试会变得很难写。现在你可以单独测 `run_reviewer()` 的输出契约，也可以单独测 LangGraph 在 `needs_revision` 或 `needs_more_evidence` 时怎么走。

### Step 3: 最后看存储边界

这个项目里有三类状态：

- LangGraph state：一次运行内部的临时状态
- PostgreSQL：跨运行保存的长期记忆和运行记录
- Redis：为了提速而存在的缓存

如果只看输出，很容易以为“都叫记忆”。真正的区别在于生命周期和用途。缓存是为了少做重复工作，长期记忆是为了让下一次任务还能记住过去的上下文。

## Next steps

你现在已经知道这个项目为什么要分层，以及每一层解决什么问题。

接下来可以继续看：

- `docs/02-langchain-vs-langgraph.md`
- `docs/03-memory-and-cache.md`
