from app.cache.redis_cache import RedisCache


class FakeRedisClient:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value


class RawRedisClient:
    def __init__(self, raw_value):
        self.raw_value = raw_value

    def get(self, key):
        return self.raw_value

    def setex(self, key, ttl, value):
        self.raw_value = value


class FailingGetRedisClient:
    def get(self, key):
        raise RuntimeError("redis get failed")


class FailingSetRedisClient:
    def get(self, key):
        return None

    def setex(self, key, ttl, value):
        raise RuntimeError("redis set failed")


def test_redis_cache_round_trip():
    cache = RedisCache(client=FakeRedisClient(), enabled=True)

    cache.set_json("planner:demo", {"topic": "Redis"}, ttl=30)

    assert cache.get_json("planner:demo") == {"topic": "Redis"}


def test_redis_cache_get_json_returns_none_when_client_get_fails():
    cache = RedisCache(client=FailingGetRedisClient(), enabled=True)

    assert cache.get_json("planner:demo") is None


def test_redis_cache_set_json_silently_degrades_when_client_setex_fails():
    cache = RedisCache(client=FailingSetRedisClient(), enabled=True)

    cache.set_json("planner:demo", {"topic": "Redis"}, ttl=30)


def test_redis_cache_get_json_returns_none_when_payload_is_not_json():
    cache = RedisCache(client=RawRedisClient(b"not-json"), enabled=True)

    assert cache.get_json("planner:demo") is None


def test_redis_cache_get_json_returns_none_when_payload_is_not_object():
    cache = RedisCache(client=RawRedisClient("[1, 2, 3]"), enabled=True)

    assert cache.get_json("planner:demo") is None
