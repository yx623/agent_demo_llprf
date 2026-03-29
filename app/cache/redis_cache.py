import json
from typing import Any


class RedisCache:
    """对 Redis 做最小封装，并在不可用时优雅降级。"""

    def __init__(self, client: Any | None, enabled: bool = True):
        self.client = client
        self.enabled = enabled and client is not None

    def get_json(self, key: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        raw = self.client.get(key)
        if raw is None:
            return None

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")

        return json.loads(raw)

    def set_json(self, key: str, value: dict[str, Any], ttl: int) -> None:
        if not self.enabled:
            return

        payload = json.dumps(value, ensure_ascii=False)
        self.client.setex(key, ttl, payload)
