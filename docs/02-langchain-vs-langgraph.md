---
title: 用一个教学任务看 LangChain 和 LangGraph 的分工
description: 通过规划、写作和审查三个环节理解单 Agent 与多 Agent 的边界。
nav_title: LangChain 与 LangGraph
---

很多初学者第一次做多智能体项目时，会把 LangChain 和 LangGraph 当成可以互相替代的工具。这个项目的写法更适合教学，因为它把两者的边界压到最清楚的形式。

这里的核心问题不是“哪个框架更强”，而是“哪个层负责什么事”。只要这个边界搞清楚，后续加记忆、缓存和恢复能力时就不容易走歪。

## Example

我们以“生成一份 LangGraph 教学提纲”为例。

先由 planner 产出计划，再由 researcher 收集材料，writer 组织教学稿，最后 reviewer 给出通过、改写或补证据的决策。

### Step 1: 让 LangChain 只负责单个 Agent 的输出契约

`app/agents/` 里的函数都围绕一件事展开：把模型调用包装成稳定的结构化输出。

例如：

- planner 输出 `PlanOutput`
- researcher 输出 `ResearchOutput`
- writer 输出 `WriterOutput`
- reviewer 输出 `ReviewOutput`

如果这一步没有结构化输出，后面的工作流只能靠字符串解析。那样一旦模型措辞变化，整个流程就会变得不稳定。

### Step 2: 让 LangGraph 只负责状态和路由

`app/graph/builder.py` 并不关心 prompt 细节。它关心的是：

- 从 `router` 开始，接到 `planner`
- 再进入 `researcher`、`writer`、`reviewer`
- reviewer 返回不同决策时，工作流应该去哪里

这一层解决的是“谁先做、谁后做、什么时候回头修改”。也正因为这样，关于循环上限、终止条件和 checkpoint 的测试都应该落在这一层。

### Step 3: 用 checkpoint 把运行过程变成可恢复对象

一旦工作流里有循环，教学时就会遇到一个问题：中断后怎么解释“从哪里继续”。这就是 checkpoint 的作用。

在本项目里，`app/db/checkpoint.py` 提供了 in-memory 与 PostgreSQL 两种 checkpointer 路径。教学演示时可以先用内存模式，再切到 PostgreSQL，让学生看到“恢复”并不是抽象概念，而是实际可保存、可读取的状态快照。

## Next steps

你现在已经知道 LangChain 负责单 Agent 契约，LangGraph 负责多 Agent 路由与恢复。

接下来可以继续看：

- `docs/03-memory-and-cache.md`
- `docs/05-walkthrough.md`
