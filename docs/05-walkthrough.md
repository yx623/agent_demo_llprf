---
title: 从命令行到接口完成一次教学演示
description: 按顺序跑通 doctor、run、resume 和 API 调用，形成完整课堂演示路径。
nav_title: 演示路径
---

前面的文档解释了项目结构，这一篇把它们串成一次可以直接照着讲的演示。目标不是覆盖所有细节，而是让你在几分钟内跑出一条完整链路。

建议在开始前先准备好 `.env`、数据库表和一条演示记忆。这样学生看到的不是空系统，而是一个已经具备最小上下文的教学环境。

## Example

这次演示会完成四件事：

1. 检查应用配置
2. 发起一次教学任务
3. 恢复刚才的任务
4. 切到 HTTP 接口重复同一动作

### Step 1: 先做环境检查

运行：

```bash
python -m app.cli doctor
```

你会看到一段 JSON，里面包含 `status` 和各项检查位。这里的重点不是“数据库已经连通”，而是先说明入口层已经接好。

### Step 2: 再发起一次任务

运行：

```bash
python -m app.cli run "Redis 教学" "解释 Redis 的作用"
```

输出里会出现 `run_id`、`status`、`current_node` 和 `final_output`。这一步适合讲“任务对象”长什么样，以及为什么 CLI 和 API 都围绕它工作。

### Step 3: 用 resume 解释恢复语义

拿上一步返回的 `run_id`，继续运行：

```bash
python -m app.cli resume <run_id>
```

如果恢复成功，输出会返回同一条任务对象。这里可以顺势引出 LangGraph checkpoint 的后续扩展点：当前示例先用内存 run 演示接口语义，后续再把它接到真实工作流恢复。

### Step 4: 切到 HTTP 入口重复相同流程

启动服务：

```bash
uvicorn app.main:app --reload
```

然后依次调用：

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/tasks/run -H 'Content-Type: application/json' -d '{"user_id":"demo-user","title":"LangGraph 教学","input_text":"请写一份 LangGraph 教学提纲"}'
curl -X POST http://127.0.0.1:8000/tasks/<run_id>/resume
```

你会发现 CLI 和 API 返回的是同一种任务对象，这正是 `TaskService` 统一入口的价值。

## Next steps

你现在已经可以独立跑完一次完整的课堂演示。

接下来可以继续做两件事：

- 把 `TaskService` 从内存实现替换成真实的 LangGraph 运行器
- 配合 PostgreSQL 和 Redis 演示长期记忆与缓存命中
