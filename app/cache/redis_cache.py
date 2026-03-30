"""Redis 缓存的最小封装层。

教学上最重要的点不是“封装得多复杂”，而是要让读者看到：
缓存失效或 Redis 不可用时，系统应当退化为“变慢”，而不是直接崩溃。
"""

import json
from typing import Any


class RedisCache:
    """对 Redis 做最小封装，并在不可用时优雅降级。"""

    def __init__(self, client: Any | None, enabled: bool = True):
        self.client = client
        self.enabled = enabled and client is not None

    def get_json(self, key: str) -> dict[str, Any] | None:
        """读取 JSON 对象。

        这里返回 `None` 的语义统一表示“缓存未命中或暂时不可用”，
        调用方不需要区分到底是 key 不存在，还是 Redis 本身故障。
        """
        if not self.enabled:
            return None

        try:
            raw = self.client.get(key)
        except Exception:
            # 缓存层失败时不要中断主流程。
            return None

        if raw is None:
            return None

        try:
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")

            payload = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            # 无法解析成 JSON 时按 miss 处理，避免把脏数据继续往上传。
            return None

        if not isinstance(payload, dict):
            return None

        return payload

    def set_json(self, key: str, value: dict[str, Any], ttl: int) -> None:
        """写入带过期时间的 JSON 缓存。"""
        if not self.enabled:
            return

        payload = json.dumps(value, ensure_ascii=False)
        try:
            self.client.setex(key, ttl, payload)
        except Exception:
            # 写缓存失败只影响性能，不应该影响主业务。
            return
