"""命令行入口。

CLI 的价值不是替代 API，而是给教学演示提供一个最短路径：
不启动 Web 服务也能观察系统返回的任务对象。
"""

import json

import typer

from app.schemas.task import TaskRequest
from app.services.task_service import TaskService

# `Typer` 把函数直接映射成子命令，适合教学时逐条演示。
app = typer.Typer(help="agent_demo_llprf 教学项目命令行入口")
service = TaskService()


@app.command()
def doctor():
    """输出应用环境检查结果。"""
    typer.echo("应用环境检查")
    typer.echo(json.dumps(service.doctor(), ensure_ascii=False, indent=2))


@app.command()
def run(title: str, input_text: str, user_id: str = "demo-user"):
    """执行一个教学任务。"""
    result = service.run_task(
        TaskRequest(user_id=user_id, title=title, input_text=input_text)
    )
    typer.echo(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))


@app.command()
def resume(run_id: str):
    """恢复一个已有任务。"""
    result = service.resume_task(run_id)
    if result is None:
        # 命令行里用退出码表达失败，比打印大段异常更利于演示。
        raise typer.Exit(code=1)
    typer.echo(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))


@app.command()
def history():
    """查看当前会话中的运行历史。"""
    payload = [item.model_dump() for item in service.list_runs()]
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


@app.command()
def memory(user_id: str = "demo-user"):
    """查看指定用户的长期记忆。"""
    payload = [item.model_dump(mode="json") for item in service.list_memory(user_id)]
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


def main():
    """供 `python -m app.cli` 调用的统一入口。"""
    app()


if __name__ == "__main__":
    main()
