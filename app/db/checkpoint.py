"""为 LangGraph 提供 checkpoint 构造入口。"""

from contextlib import contextmanager
from importlib import import_module

from langgraph.checkpoint.memory import MemorySaver

from app.core.config import Settings


def _normalize_postgres_conn_string(postgres_dsn: str) -> str:
    """把 SQLAlchemy 风格 DSN 转成 LangGraph 更易接受的形式。"""
    if postgres_dsn.startswith("postgresql+psycopg://"):
        return postgres_dsn.replace("postgresql+psycopg://", "postgresql://", 1)
    return postgres_dsn


@contextmanager
def build_checkpointer(settings: Settings, *, in_memory: bool = False):
    """构造 LangGraph checkpointer。

    教学时通常先用内存版理解 checkpoint 概念，再切到 PostgreSQL
    观察持久化恢复。因此这里同时提供两种模式。
    """
    if in_memory:
        yield MemorySaver()
        return

    # 延迟导入可以避免在没有安装 postgres extra 的环境里，
    # 仅仅因为导入模块就直接失败。
    postgres_module = import_module("langgraph.checkpoint.postgres")
    postgres_saver = postgres_module.PostgresSaver
    conn_string = _normalize_postgres_conn_string(settings.postgres_dsn)

    with postgres_saver.from_conn_string(conn_string) as saver:
        # 首次使用时确保 LangGraph 需要的表结构已经就绪。
        saver.setup()
        yield saver
