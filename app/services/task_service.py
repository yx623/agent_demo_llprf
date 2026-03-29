from uuid import uuid4

from app.schemas.memory import MemoryView
from app.schemas.task import TaskRequest, TaskRunView


class TaskService:
    """统一封装 CLI 与 API 共享的任务动作。"""

    def __init__(self, memory_service=None):
        self.memory_service = memory_service
        self._runs: dict[str, TaskRunView] = {}

    def doctor(self) -> dict:
        return {
            "status": "ok",
            "checks": {
                "api_config": "configured",
                "database": "pending-runtime-check",
                "redis": "pending-runtime-check",
            },
        }

    def run_task(self, request: TaskRequest) -> TaskRunView:
        run_id = str(uuid4())
        run = TaskRunView(
            run_id=run_id,
            status="succeeded",
            current_node="finalize",
            final_output=f"# 任务结果\n\n{request.input_text}",
        )
        self._runs[run_id] = run
        return run

    def get_run(self, run_id: str) -> TaskRunView | None:
        return self._runs.get(run_id)

    def list_memory(self, user_id: str) -> list[MemoryView]:
        if self.memory_service is None:
            return []

        items = self.memory_service.list_by_user(user_id)
        return [
            MemoryView(
                id=item.id,
                namespace=item.namespace,
                key=item.key,
                content=item.content,
                created_at=item.created_at,
            )
            for item in items
        ]
