from app.core.config import get_settings
from app.db.base import Base
from app.db.session import build_engine


def main() -> None:
    settings = get_settings()
    engine = build_engine(settings)
    Base.metadata.create_all(engine)
    print("数据库初始化完成")


if __name__ == "__main__":
    main()
