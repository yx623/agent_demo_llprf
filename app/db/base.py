"""SQLAlchemy 基础声明。

这里统一声明命名规范，目的是让自动生成的约束名在数据库里
保持稳定，便于教学时观察表结构，也便于后续迁移工具识别差异。
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """所有 ORM 模型的共同基类。"""
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
