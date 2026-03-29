import json

import typer

from app.schemas.task import TaskRequest
from app.services.task_service import TaskService

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


def main():
    app()


if __name__ == "__main__":
    main()
