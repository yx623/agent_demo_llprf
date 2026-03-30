import sys
from pathlib import Path

# 允许直接以脚本方式运行，而不是必须先安装成包。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.db.session import build_session_factory
from app.memory.long_term import LongTermMemoryService


def main() -> None:
    """写入一条最小演示记忆。"""
    settings = get_settings()
    session_factory = build_session_factory(settings)
    memory_service = LongTermMemoryService(session_factory)
    memory_service.save(
        user_id="demo-user",
        namespace="preference",
        key="language",
        content="默认使用中文回答，并采用教学型结构。",
        source_run_id=None,
    )
    print("演示数据写入完成")


if __name__ == "__main__":
    main()
