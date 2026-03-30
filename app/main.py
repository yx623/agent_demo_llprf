"""FastAPI 入口。

这个文件只负责 HTTP 协议层，不直接承载业务编排逻辑。
所有动作最终都委托给 `TaskService`，这样 CLI 与 API 才能保持一致。
"""

from fastapi import FastAPI, HTTPException

from app.schemas.task import TaskRequest
from app.services.task_service import TaskService

# 在教学项目里直接使用模块级 service，方便快速演示。
app = FastAPI(title="agent_demo_llprf")
service = TaskService()


@app.get("/health")
async def health():
    """健康检查接口。"""
    return service.doctor()


@app.post("/tasks/run")
async def run_task(request: TaskRequest):
    """发起任务。"""
    return service.run_task(request)


@app.post("/tasks/{run_id}/resume")
async def resume_task(run_id: str):
    """恢复已有任务。"""
    run = service.resume_task(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return run


@app.get("/tasks/{run_id}")
async def get_task(run_id: str):
    """读取指定任务。"""
    run = service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return run


@app.get("/memory")
async def list_memory(user_id: str = "demo-user"):
    """读取指定用户的长期记忆。"""
    return service.list_memory(user_id)
