from app.cache.redis_cache import RedisCache


class FakeRedisClient:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value


def test_redis_cache_round_trip():
    cache = RedisCache(client=FakeRedisClient(), enabled=True)

    cache.set_json("planner:demo", {"topic": "Redis"}, ttl=30)

    assert cache.get_json("planner:demo") == {"topic": "Redis"}
