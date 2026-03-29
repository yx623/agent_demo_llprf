from contextlib import contextmanager

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

from app.core.config import Settings


@contextmanager
def build_checkpointer(settings: Settings, *, in_memory: bool = False):
    if in_memory:
        yield MemorySaver()
        return

    with PostgresSaver.from_conn_string(settings.postgres_dsn) as saver:
        saver.setup()
        yield saver
