import redis
from app.core.config import settings

_redis = None

def get_redis():
    global _redis
    if _redis is None:
        try:
            _redis = redis.StrictRedis.from_url(settings.REDIS_URL)
            _redis.ping()  # test connection
            print("✅ Redis connected successfully!")
        except Exception as e:
            print("⚠️ Redis connection failed, continuing without Redis:", e)
            _redis = None
    return _redis
