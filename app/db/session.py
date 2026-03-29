from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings


def build_engine(settings: Settings) -> Engine:
    return create_engine(settings.postgres_dsn, pool_pre_ping=True, future=True)


def build_session_factory(settings: Settings) -> sessionmaker:
    engine = build_engine(settings)
    return sessionmaker(bind=engine, expire_on_commit=False)
