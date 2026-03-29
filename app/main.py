from fastapi import FastAPI, HTTPException

from app.schemas.task import TaskRequest
from app.services.task_service import TaskService

app = FastAPI(title="agent_demo_llprf")
service = TaskService()


@app.get("/health")
async def health():
    return service.doctor()


@app.post("/tasks/run")
async def run_task(request: TaskRequest):
    return service.run_task(request)


@app.get("/tasks/{run_id}")
async def get_task(run_id: str):
    run = service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return run


@app.get("/memory")
async def list_memory(user_id: str = "demo-user"):
    return service.list_memory(user_id)
