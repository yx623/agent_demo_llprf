"""数据库连接与 Session 工厂。"""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings


def build_engine(settings: Settings) -> Engine:
    """根据配置创建 SQLAlchemy Engine。"""
    return create_engine(settings.postgres_dsn, pool_pre_ping=True, future=True)


def build_session_factory(settings: Settings) -> sessionmaker:
    """返回会话工厂。

    这里把 `expire_on_commit=False` 固定下来，避免教学时在 commit 后
    读取对象属性又触发额外查询，让示例行为更容易预测。
    """
    engine = build_engine(settings)
    return sessionmaker(bind=engine, expire_on_commit=False)
