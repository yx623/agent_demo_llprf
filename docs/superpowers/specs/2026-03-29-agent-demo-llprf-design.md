# agent_demo_llprf 设计说明

## 1. 项目目标

构建一个偏教学、偏进阶的多智能体示例项目，用真实 API 展示 LangChain 与 LangGraph 在实际应用中的不同职责，同时清晰演示短期状态、长期记忆与缓存之间的区别。

项目运行环境固定为本机 `conda activate agent`，并连接当前已存在的本地 Docker 服务：

- PostgreSQL：`localhost:5432`
- Redis：`localhost:6379`

仓库为独立 git 项目，根目录位于 `agent_demo_llprf`，远端仓库地址为：

- `https://github.com/yx623/agent_demo_llprf.git`

## 2. 教学定位

这不是一个泛化的企业级智能体平台，而是一个面向中级学习者的聚焦型教学项目。默认读者已经具备基础 Python 能力，并且知道如何调用 LLM API，现在需要一个可运行、可拆解、可讲解的项目来回答这些问题：

- LangChain 在单个智能体内部应该负责什么
- LangGraph 在多个智能体之间应该负责什么
- 为什么缓存和记忆不是一回事
- 为什么同一套 agent 内核可以同时服务 CLI 和 FastAPI
- 为什么持久化与可恢复能力会改变 agent 系统的设计方式

项目整体以“讲清楚”为第一目标，不追求功能堆叠。每个模块都应服务一个明确的教学点。

## 3. Demo 主题

本项目实现一个“多智能体研究任务助手”。

用户可以提交类似下面的任务：

- “总结 Redis 在 Agent 系统中的作用，并生成一页教学提纲。”
- “写一份 LangChain 与 LangGraph 的对比草稿，用于工作坊幻灯片。”

系统会将请求交给一组角色清晰的 agent 协同处理，最终产出经过审校的结果。

首版不强调实时联网搜索，重点放在以下内容：

- 多智能体编排
- 记忆读取与写入
- 缓存命中与降级
- 持久化与恢复
- LangChain / LangGraph 的职责分工

## 4. 用户入口

项目通过两种入口暴露同一套应用核心：

- CLI
- FastAPI

### CLI

CLI 将提供偏教学的命令，例如：

- `doctor`：检查环境、数据库、Redis 与模型配置
- `run`：创建并执行一个任务
- `resume`：从 checkpoint 恢复一次任务运行
- `history`：查看历史运行记录
- `memory`：查看长期记忆条目

### FastAPI

HTTP API 将提供如下核心接口：

- `GET /health`
- `POST /tasks/run`
- `POST /tasks/{run_id}/resume`
- `GET /tasks/{run_id}`
- `GET /memory`

CLI 与 FastAPI 必须共用同一层应用服务，以便在教学中明确说明“入口层”和“agent 内核”是解耦的。

## 5. 总体架构

系统分为五层。

### 5.1 入口层

CLI 与 FastAPI 只负责输入输出和请求转换，不直接承载 agent 编排逻辑。

### 5.2 应用层

通过 `TaskService` 统一封装任务执行、任务恢复、历史查询、记忆查询等应用动作。

### 5.3 编排层

LangGraph 负责：

- 多智能体图结构
- 共享状态
- 节点流转
- 条件分支
- checkpoint
- 可恢复执行

### 5.4 单 Agent 能力层

LangChain 负责每个 agent 内部能力的组织：

- 提示词构造
- 模型调用
- 结构化输出
- 工具调用
- 需要时接入轻量记忆适配

### 5.5 基础设施层

- PostgreSQL：保存长期数据与图状态持久化数据
- Redis：保存缓存与短生命周期加速数据

## 6. LangChain 与 LangGraph 的边界

这个项目必须刻意把两者的职责边界讲清楚。

### LangChain 负责的内容

- 封装单个 agent
- 定义提示词模板和消息结构
- 定义模型包装与结构化输出格式
- 接入轻量工具，例如记忆检索工具
- 组织单 agent 的推理行为

### LangGraph 负责的内容

- 定义工作流图
- 管理共享状态
- 控制分支与循环
- 约束修订次数
- 支持 checkpoint 持久化与恢复

代码结构和教学文档都必须围绕这个边界展开，避免让学习者误以为 LangChain 与 LangGraph 只是两个可互换框架。

## 7. Agent 角色

首版采用 4 个 LLM 驱动的 agent，再加 1 个路由节点。

### `router`

用于判断当前请求属于哪一类：

- 新任务
- 恢复已有任务
- 读取历史或记忆的查询型请求

### `planner`

把用户需求转成结构化计划，至少包含：

- 任务目标
- 执行步骤
- 完成标准

### `researcher`

基于现有上下文、历史记忆和内部工具整理支撑材料，不强调联网搜索，重点展示“从系统内部知识与记忆中取材”。

### `writer`

根据计划和研究笔记生成结果草稿。

### `reviewer`

负责审校草稿，并给出以下三种之一的结论：

- `pass`
- `needs_revision`
- `needs_more_evidence`

## 8. 图流程设计

初始图结构为：

`router -> planner -> researcher -> writer -> reviewer`

`reviewer` 的条件分支如下：

- `pass -> finalize`
- `needs_revision -> writer`
- `needs_more_evidence -> researcher`

为避免无限循环，工作流必须限制最大修订轮数。首版实现中，修订轮数上限设为 `2`。

## 9. 状态、记忆与缓存

本项目的重要教学目标之一，是把三个经常被混淆的概念拆开讲清楚。

### 9.1 短期运行状态

存放在 LangGraph state 中，示例包括：

- 用户输入
- 当前计划
- 研究笔记
- 当前草稿
- 审校结果
- 当前迭代次数

这是“一次运行内部的上下文”，不是跨会话长期记忆。

### 9.2 长期记忆

持久化到 PostgreSQL，示例包括：

- 用户偏好的输出风格
- 历史任务的摘要
- 被确认可复用的知识片段
- 产物元数据

长期记忆跨运行存在，可以在后续任务中查询和复用。

### 9.3 缓存

存放在 Redis，示例包括：

- 相同输入下的 planner 结果缓存
- researcher 阶段的摘要缓存
- 最终结果缓存
- 最近会话的短生命周期摘要缓存

缓存服务于性能优化，不是系统事实来源。

## 10. 持久化设计

PostgreSQL 为必需依赖，用于保存：

- 用户信息
- 任务运行记录
- 运行事件或消息
- 长期记忆条目
- 生成产物
- LangGraph checkpoint

Redis 默认启用，但在运行时属于可降级依赖。若 Redis 不可用，系统应关闭缓存能力，但主流程仍应继续可用。

## 11. 数据库与服务假设

当前教学环境已经提供：

- PostgreSQL 容器 `my-postgres`
- Redis 容器 `my-redis`

项目应使用独立数据库名，例如 `agent_demo_llprf`。

所有连接配置都通过 `.env` 管理，不允许写死在代码中。

## 12. 错误处理策略

这个项目应该强调“可观察、可恢复、可解释”的失败行为。

- PostgreSQL 连接失败时，应用启动直接失败
- Redis 连接失败时，应用进入降级模式，但仍可运行主流程
- LLM 调用采用有限次重试
- 任务失败信息要写入数据库
- 在条件允许时，每个节点都记录耗时、缓存命中等元数据
- 中断的运行可以基于 checkpoint 恢复

## 13. 测试策略

运行时使用真实 API，但自动化测试不依赖真实 API。

### 单元测试

使用 fake 或 mock chat model 测试：

- 路由逻辑
- 节点状态迁移
- state 更新
- Redis 缓存封装
- PostgreSQL 记忆仓储

### 图编排测试

重点覆盖三条核心路径：

- `pass` 主路径
- `needs_revision` 重写路径
- `needs_more_evidence` 补充材料路径

### API 测试

覆盖任务执行、任务查询、记忆查询、恢复任务等核心接口。

### CLI smoke test

覆盖核心命令：

- `doctor`
- `run`
- `resume`
- `history`

### 手动真实 API smoke test

在 README 中保留一条人工演示链路，但不纳入默认自动化测试。

## 14. 建议目录结构

```text
agent_demo_llprf/
├─ README.md
├─ .env.example
├─ .gitignore
├─ pyproject.toml
├─ alembic.ini
├─ docs/
│  ├─ 01-overview.md
│  ├─ 02-langchain-vs-langgraph.md
│  ├─ 03-memory-and-cache.md
│  ├─ 04-cli-and-api.md
│  ├─ 05-walkthrough.md
│  └─ superpowers/
│     └─ specs/
├─ app/
│  ├─ main.py
│  ├─ cli.py
│  ├─ core/
│  ├─ agents/
│  ├─ graph/
│  ├─ memory/
│  ├─ cache/
│  ├─ db/
│  ├─ schemas/
│  ├─ services/
│  └─ tools/
├─ scripts/
└─ tests/
```

这个结构是为“教学可读性”服务的，不是为大规模团队组织做的最优分层。

## 15. 第一阶段范围

第一阶段实现包含：

- 独立仓库初始化
- 本地配置与依赖脚手架
- CLI 与 FastAPI 共用的应用服务层
- PostgreSQL 持久化任务运行与长期记忆
- 支持降级的 Redis 缓存封装
- 具备初始 agent 角色的 LangGraph 工作流
- CLI 命令与 FastAPI 接口
- 基础文档与测试

第一阶段明确不做：

- 前端页面
- 用户认证与多租户
- 大量外部工具生态接入
- 把实时联网搜索作为核心能力
- 复杂 observability 平台接入

## 16. Git 工作流

git 管理本身也是教学内容的一部分。

### 分支策略

- `main`：始终保持阶段性可运行
- `dev`：日常集成分支
- `feature/*`：围绕单一教学目标的短分支

### 示例功能分支

- `feature/project-scaffold`
- `feature/postgres-memory`
- `feature/redis-cache`
- `feature/langgraph-flow`
- `feature/fastapi-cli-entry`

### 提交粒度

提交应尽量小，并且具备教学含义，例如：

- `chore: initialize teaching project scaffold`
- `feat: add postgres persistence for task runs`
- `feat: add redis cache for planner node`
- `feat: implement langgraph revision workflow`
- `feat: expose task runner via cli and fastapi`
- `docs: add memory and cache walkthrough`

## 17. 成功标准

如果学习者能够做到以下几点，就说明项目达成目标：

- 既能通过 CLI 运行任务，也能通过 FastAPI 运行任务
- 能在 PostgreSQL 中查看运行历史
- 能观察 Redis 缓存行为
- 能从代码与文档中理解 LangChain 与 LangGraph 的职责划分
- 能理解短期状态、长期记忆与缓存的区别
- 能从 checkpoint 恢复一次被中断的工作流

## 18. 下一步

本设计文档在仓库中确认后，下一步是先编写实现计划，再开始写应用代码。
