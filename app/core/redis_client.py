from redis import Redis
from app.core.config import settings
from datetime import time

_redis = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        for _ in range(5):
            try:
                _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
                _redis.ping()
                break
            except ConnectionError:
                time.sleep(1)
    return _redis
