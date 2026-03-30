---
title: 系统学习 agent_demo_llprf
description: 按项目结构、阅读顺序和动手实验顺序系统理解这个教学型多智能体项目。
nav_title: 系统学习指南
---

这份指南解决一个具体问题：第一次打开 `agent_demo_llprf` 时，应该先看哪里，再看哪里，才不会把 LangChain、LangGraph、服务层、数据库和缓存混成一团。这个仓库的文件已经不算多，但如果没有顺序，初学者很容易在 `app/` 里来回跳转，最后只记住零散片段。

本指南把学习过程拆成四步。你会先建立目录级心智模型，再读单 Agent 层，再读多 Agent 编排与服务入口，最后通过动手实验把概念串起来。这样阅读时每一层只解决一个问题。

## Example

把这个项目想成一个“中文教学稿生成器”。用户给出一个主题，系统先规划，再研究，再写作，再审校，最后通过 CLI 或 API 把结果返回给用户。

阅读时请同时打开仓库根目录、`app/` 目录和 `docs/` 目录。你会从“看结构”开始，而不是直接钻进某个函数。

### Step 1: 先用目录结构建立全局地图

先看这棵简化后的目录树：

```text
agent_demo_llprf/
├── app/
│   ├── agents/        # 单个 Agent 的 LangChain 封装
│   ├── graph/         # 多 Agent 的 LangGraph 工作流
│   ├── services/      # CLI 与 API 共享的应用服务层
│   ├── db/            # PostgreSQL 相关模型、session、checkpoint
│   ├── memory/        # 长期记忆服务
│   ├── cache/         # Redis 缓存封装
│   ├── schemas/       # Pydantic 输入输出模型
│   ├── tools/         # LangChain 工具
│   ├── cli.py         # 命令行入口
│   └── main.py        # FastAPI 入口
├── docs/              # 教学文档与学习材料
├── scripts/           # 初始化数据库、写入演示数据、启动演示
└── tests/             # 单元测试与集成测试
```

这一步的目标不是记住所有文件，而是回答三个问题：

- 单 Agent 在哪里定义
- 多 Agent 编排在哪里定义
- 用户是从哪里进入系统

如果这三个问题答不出来，后面读代码时就会不断迷路。

### Step 2: 再读单 Agent 层，理解 LangChain 负责什么

第二步只读这些文件：

- [common.py](/home/yx/myproject/Agent/agent_demo_llprf/app/agents/common.py)
- [planner.py](/home/yx/myproject/Agent/agent_demo_llprf/app/agents/planner.py)
- [researcher.py](/home/yx/myproject/Agent/agent_demo_llprf/app/agents/researcher.py)
- [writer.py](/home/yx/myproject/Agent/agent_demo_llprf/app/agents/writer.py)
- [reviewer.py](/home/yx/myproject/Agent/agent_demo_llprf/app/agents/reviewer.py)
- [task.py](/home/yx/myproject/Agent/agent_demo_llprf/app/schemas/task.py)

读这一层时只盯住一个问题：LangChain 在这里负责什么。答案应该是“模型调用、结构化输出和工具封装”，而不是“多 Agent 路由”。

可观察的阅读顺序是：

1. 先看 `schemas/task.py`，理解每个 Agent 要返回什么结构。
2. 再看 `agents/*.py`，理解 prompt 如何被包装成结构化输出。
3. 最后看 `tools/memory_lookup.py`，理解工具是怎么接进 Agent 的。

如果你读完后能说出 `PlanOutput`、`ResearchOutput`、`WriterOutput`、`ReviewOutput` 分别服务于哪个 Agent，这一步就完成了。

### Step 3: 然后读工作流和服务层，理解 LangGraph 与双入口

第三步只读这些文件：

- [state.py](/home/yx/myproject/Agent/agent_demo_llprf/app/graph/state.py)
- [nodes.py](/home/yx/myproject/Agent/agent_demo_llprf/app/graph/nodes.py)
- [builder.py](/home/yx/myproject/Agent/agent_demo_llprf/app/graph/builder.py)
- [task_service.py](/home/yx/myproject/Agent/agent_demo_llprf/app/services/task_service.py)
- [cli.py](/home/yx/myproject/Agent/agent_demo_llprf/app/cli.py)
- [main.py](/home/yx/myproject/Agent/agent_demo_llprf/app/main.py)

这一层解决两个摩擦点。

第一个摩擦点是：多个 Agent 之间如何衔接。`builder.py` 通过 LangGraph 把 planner、researcher、writer、reviewer 串成一个有回环、有终止条件的工作流。

第二个摩擦点是：CLI 和 API 为什么不会各写一套逻辑。答案在 `TaskService`。它把运行任务、恢复任务、列出历史、读取记忆这些动作统一起来，入口层只负责协议转换。

读完这一层后，你应该能回答：

- 为什么 `reviewer` 返回 `needs_more_evidence` 会回到研究节点
- 为什么 `CLI` 和 `FastAPI` 都依赖 `TaskService`
- 为什么非法 `review decision` 会立刻报错而不是静默重试

### Step 4: 最后用数据层、缓存和脚本做动手实验

最后再读这些文件并动手跑一遍：

- [models.py](/home/yx/myproject/Agent/agent_demo_llprf/app/db/models.py)
- [session.py](/home/yx/myproject/Agent/agent_demo_llprf/app/db/session.py)
- [checkpoint.py](/home/yx/myproject/Agent/agent_demo_llprf/app/db/checkpoint.py)
- [long_term.py](/home/yx/myproject/Agent/agent_demo_llprf/app/memory/long_term.py)
- [redis_cache.py](/home/yx/myproject/Agent/agent_demo_llprf/app/cache/redis_cache.py)
- [init_db.py](/home/yx/myproject/Agent/agent_demo_llprf/scripts/init_db.py)
- [seed_demo_data.py](/home/yx/myproject/Agent/agent_demo_llprf/scripts/seed_demo_data.py)
- [run_demo.sh](/home/yx/myproject/Agent/agent_demo_llprf/scripts/run_demo.sh)

推荐实验顺序：

1. `python scripts/init_db.py`
2. `python scripts/seed_demo_data.py`
3. `python -m app.cli doctor`
4. `python -m app.cli run "Redis 教学" "解释 Redis 的作用"`
5. `python -m app.cli history`
6. `python -m app.cli memory`
7. `uvicorn app.main:app --reload`

这一步的观察重点是三类状态：

- LangGraph state 只存在于一次运行内
- PostgreSQL 负责长期记忆和运行记录
- Redis 负责缓存命中和优雅降级

## Next steps

你现在已经有一条完整的阅读顺序，可以从全局结构一路走到具体实验。

接下来建议继续看：

- [项目概览](/home/yx/myproject/Agent/agent_demo_llprf/docs/01-overview.md)
- [LangChain 与 LangGraph 的分工](/home/yx/myproject/Agent/agent_demo_llprf/docs/02-langchain-vs-langgraph.md)
- [记忆与缓存](/home/yx/myproject/Agent/agent_demo_llprf/docs/03-memory-and-cache.md)
