import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Artifact, MemoryItem, RunStatus, TaskRun


def test_task_run_memory_and_artifact_can_persist():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    with SessionLocal() as session:
        run = TaskRun(
            user_id="demo-user",
            title="Redis 教学任务",
            input_text="解释 Redis 的作用",
            status=RunStatus.RUNNING,
            current_node="planner",
        )
        session.add(run)
        session.flush()

        memory = MemoryItem(
            user_id="demo-user",
            namespace="preference",
            key="tone",
            content="请使用教学型中文输出",
            source_run_id=run.id,
        )
        artifact = Artifact(
            run_id=run.id,
            artifact_type="draft",
            content="# Redis 教学提纲",
        )
        session.add_all([memory, artifact])
        session.commit()

    with SessionLocal() as session:
        saved_run = session.query(TaskRun).one()
        saved_memory = session.query(MemoryItem).one()
        saved_artifact = session.query(Artifact).one()

    assert saved_run.title == "Redis 教学任务"
    assert saved_memory.namespace == "preference"
    assert saved_artifact.artifact_type == "draft"


def test_task_run_status_persists_enum_value():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    with SessionLocal() as session:
        session.add(
            TaskRun(
                user_id="demo-user",
                title="状态测试",
                input_text="检查枚举持久化值",
                status=RunStatus.RUNNING,
            )
        )
        session.commit()

    with engine.connect() as connection:
        saved_status = connection.execute(text("SELECT status FROM task_runs")).scalar_one()

    assert saved_status == "running"


def test_task_run_status_rejects_invalid_string():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    with SessionLocal() as session:
        session.add(
            TaskRun(
                user_id="demo-user",
                title="非法状态测试",
                input_text="检查非法状态是否被拒绝",
                status="bogus",
            )
        )

        with pytest.raises((StatementError, LookupError)):
            session.commit()
