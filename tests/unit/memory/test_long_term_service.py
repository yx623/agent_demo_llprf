from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.memory.long_term import LongTermMemoryService


def test_long_term_memory_save_and_list():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    service = LongTermMemoryService(SessionLocal)

    service.save(
        user_id="demo-user",
        namespace="preference",
        key="style",
        content="回答尽量使用条理清晰的中文",
        source_run_id=None,
    )

    memories = service.list_by_user("demo-user")

    assert len(memories) == 1
    assert memories[0].key == "style"
