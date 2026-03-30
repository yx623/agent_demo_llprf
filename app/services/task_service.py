"""CLI 与 FastAPI 共用的应用服务层。

这个文件是教学项目里非常关键的一层，因为它把“入口协议”和
“任务动作”解耦了。CLI 与 API 都依赖这里，而不是直接操作 Agent 或数据库。
"""

from uuid import uuid4

from app.schemas.memory import MemoryView
from app.schemas.task import TaskRequest, TaskRunView


class TaskService:
    """统一封装 CLI 与 API 共享的任务动作。"""

    def __init__(self, memory_service=None):
        self.memory_service = memory_service
        self._runs: dict[str, TaskRunView] = {}

    def doctor(self) -> dict:
        """返回一个最小的环境检查视图。

        这里故意不直接探测数据库和 Redis，可先让读者理解“服务层统一输出”
        这件事，再在后续实验里扩展成真实健康检查。
        """
        return {
            "status": "ok",
            "checks": {
                "api_config": "configured",
                "database": "not_checked",
                "redis": "not_checked",
            },
        }

    def run_task(self, request: TaskRequest) -> TaskRunView:
        """创建一条最小运行记录并返回结果。

        当前实现还是内存版，主要用于教学演示服务层形状。
        后续完全可以把这里替换成真实 LangGraph 执行入口。
        """
        run_id = str(uuid4())
        run = TaskRunView(
            run_id=run_id,
            status="succeeded",
            current_node="finalize",
            final_output=f"# 任务结果\n\n{request.input_text}",
        )
        self._runs[run_id] = run
        return run

    def resume_task(self, run_id: str) -> TaskRunView | None:
        """恢复一条已存在的任务。

        这里先演示接口语义：什么叫“恢复”。下一步再把它接到真实
        checkpointer 或数据库恢复逻辑。
        """
        return self._runs.get(run_id)

    def get_run(self, run_id: str) -> TaskRunView | None:
        """按运行 ID 查询任务。"""
        return self._runs.get(run_id)

    def list_runs(self) -> list[TaskRunView]:
        """列出当前内存中的运行历史。"""
        return list(self._runs.values())

    def list_memory(self, user_id: str) -> list[MemoryView]:
        """列出指定用户的长期记忆。"""
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
