import sys
from pathlib import Path

# 允许从仓库根目录直接执行 `python scripts/init_db.py`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.db.base import Base
from app.db import models as _models
from app.db.session import build_engine


def main() -> None:
    """初始化数据库表结构。"""
    settings = get_settings()
    engine = build_engine(settings)
    # 导入 models 的目的是确保所有 ORM 模型都已经注册到 Base.metadata。
    Base.metadata.create_all(engine)
    print("数据库初始化完成")


if __name__ == "__main__":
    main()
