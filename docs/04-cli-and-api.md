---
title: 让 CLI 和 API 共用同一套任务内核
description: 通过 TaskService 理解双入口项目如何避免逻辑分叉。
nav_title: CLI 与 API
---

教学项目经常会同时提供 CLI 和 Web API。最容易出问题的地方，是这两个入口各自复制一份业务逻辑，结果测试和行为逐渐分叉。

本项目把这个问题处理得很直接。CLI 和 FastAPI 都不直接操作 Agent 编排，而是统一调用 `TaskService`。

## Example

我们要同时支持三类动作：健康检查、发起任务、恢复任务。

如果把这些动作分别写在 `app/cli.py` 和 `app/main.py` 里，后续一旦新增参数或恢复逻辑，两边就很难保持一致。

### Step 1: 先把动作收拢到 TaskService

`TaskService` 当前提供：

- `doctor()`
- `run_task()`
- `resume_task()`
- `get_run()`
- `list_runs()`
- `list_memory()`

这样入口层只需要做参数接收和结果输出，不需要知道内部任务对象怎么组织。

### Step 2: 让 FastAPI 只负责 HTTP 协议

`app/main.py` 的职责很克制。它只做三件事：

- 接收请求
- 调用 `TaskService`
- 在找不到任务时返回 `404`

如果你以后把 `TaskService` 从内存实现切到真实数据库实现，FastAPI 路由基本不用动。

### Step 3: 让 CLI 只负责终端交互

`app/cli.py` 和 API 的关系是平行入口，而不是另一套业务实现。它只负责把结果格式化成 JSON 输出到终端。

这意味着你在课堂上既可以演示：

- `python -m app.cli doctor`
- `python -m app.cli history`

也可以演示：

- `GET /health`
- `POST /tasks/run`
- `POST /tasks/{run_id}/resume`

两边看到的是同一批任务对象。

## Next steps

你现在已经知道为什么 CLI 和 API 要共享同一层服务对象。

接下来可以继续看：

- `docs/05-walkthrough.md`
- `README.md`
