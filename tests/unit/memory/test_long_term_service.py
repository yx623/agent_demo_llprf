from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import MemoryItem
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


def test_render_for_prompt_returns_default_message_when_no_memories():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    service = LongTermMemoryService(SessionLocal)

    assert service.render_for_prompt("demo-user") == "暂无长期记忆。"


def test_render_for_prompt_includes_saved_memory():
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

    rendered = service.render_for_prompt("demo-user")

    assert "- [preference] style: 回答尽量使用条理清晰的中文" in rendered


def test_long_term_memory_list_by_user_orders_newer_item_first_when_timestamps_tie():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    service = LongTermMemoryService(SessionLocal)

    older = service.save(
        user_id="demo-user",
        namespace="preference",
        key="older",
        content="旧记忆",
        source_run_id=None,
    )
    newer = service.save(
        user_id="demo-user",
        namespace="preference",
        key="newer",
        content="新记忆",
        source_run_id=None,
    )

    tied_timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with SessionLocal() as session:
        session.get(MemoryItem, older.id).created_at = tied_timestamp
        session.get(MemoryItem, newer.id).created_at = tied_timestamp
        session.commit()

    memories = service.list_by_user("demo-user")

    assert [item.key for item in memories] == ["newer", "older"]


def test_render_for_prompt_keeps_newer_item_first_when_timestamps_tie():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    service = LongTermMemoryService(SessionLocal)

    older = service.save(
        user_id="demo-user",
        namespace="preference",
        key="older",
        content="旧记忆",
        source_run_id=None,
    )
    newer = service.save(
        user_id="demo-user",
        namespace="preference",
        key="newer",
        content="新记忆",
        source_run_id=None,
    )

    tied_timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with SessionLocal() as session:
        session.get(MemoryItem, older.id).created_at = tied_timestamp
        session.get(MemoryItem, newer.id).created_at = tied_timestamp
        session.commit()

    rendered = service.render_for_prompt("demo-user")

    assert rendered.splitlines()[:2] == [
        "- [preference] newer: 新记忆",
        "- [preference] older: 旧记忆",
    ]
