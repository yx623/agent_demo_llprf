"""数据库模型定义。

这个文件对应教学项目里的“持久化边界”：哪些信息只存在于一次运行中，
哪些信息会被保存到 PostgreSQL，读者主要从这里建立直觉。
"""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RunStatus(str, Enum):
    """任务运行状态枚举。"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TaskRun(Base):
    """一次任务执行的主记录。

    它保存的是“运行视角”的信息，例如标题、输入、当前节点、最终输出，
    方便教学时解释任务是如何从请求演变成结果的。
    """

    __tablename__ = "task_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(255))
    input_text: Mapped[str] = mapped_column(Text)
    status: Mapped[RunStatus] = mapped_column(
        SqlEnum(
            RunStatus,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            validate_strings=True,
            native_enum=False,
        ),
        default=RunStatus.PENDING,
    )
    current_node: Mapped[str | None] = mapped_column(String(64), default=None)
    final_output: Mapped[str | None] = mapped_column(Text, default=None)
    error_message: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class MemoryItem(Base):
    """长期记忆表。

    每条记录都带有用户、命名空间和键，便于后续扩展出不同类型的
    记忆，例如偏好、事实、历史摘要。
    """

    __tablename__ = "memory_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    namespace: Mapped[str] = mapped_column(String(64), index=True)
    key: Mapped[str] = mapped_column(String(128), index=True)
    content: Mapped[str] = mapped_column(Text)
    source_run_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("task_runs.id"),
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Artifact(Base):
    """任务运行过程中产生的附属产物。

    当前项目还没有把 artifacts 完整接入服务层，但模型已经准备好，
    后续可以用于保存中间草稿、研究结果或审校意见。
    """

    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("task_runs.id"), index=True)
    artifact_type: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
