from contextlib import contextmanager
from importlib import import_module

from langgraph.checkpoint.memory import MemorySaver

from app.core.config import Settings


def _normalize_postgres_conn_string(postgres_dsn: str) -> str:
    if postgres_dsn.startswith("postgresql+psycopg://"):
        return postgres_dsn.replace("postgresql+psycopg://", "postgresql://", 1)
    return postgres_dsn


@contextmanager
def build_checkpointer(settings: Settings, *, in_memory: bool = False):
    if in_memory:
        yield MemorySaver()
        return

    postgres_module = import_module("langgraph.checkpoint.postgres")
    postgres_saver = postgres_module.PostgresSaver
    conn_string = _normalize_postgres_conn_string(settings.postgres_dsn)

    with postgres_saver.from_conn_string(conn_string) as saver:
        saver.setup()
        yield saver
