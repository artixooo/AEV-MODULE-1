import time
import json
import logging
from typing import Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class PolicyCacheService:
    def __init__(self, ttl: int = settings.POLICY_CACHE_TTL):
        self.ttl = ttl
        self.memory_cache = {}
        self.redis_client = None
        self._init_redis()

    def _init_redis(self):
        try:
            import redis
            self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=1)
            self.redis_client.ping()
            logger.info("Connected to Redis cache for Policy Service")
        except Exception as e:
            logger.info(f"Redis not available ({e}), falling back to internal in-memory TTL cache")
            self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        if self.redis_client:
            try:
                val = self.redis_client.get(f"policy:{key}")
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")

        # Fallback to memory cache
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() < entry["expires_at"]:
                return entry["value"]
            else:
                del self.memory_cache[key]
        return None

    def set(self, key: str, value: Any, custom_ttl: Optional[int] = None):
        ttl = custom_ttl if custom_ttl is not None else self.ttl
        if self.redis_client:
            try:
                self.redis_client.setex(f"policy:{key}", ttl, json.dumps(value))
                return
            except Exception as e:
                logger.warning(f"Redis set error: {e}")

        # Fallback to memory cache
        self.memory_cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl
        }

    def invalidate_all(self):
        if self.redis_client:
            try:
                keys = self.redis_client.keys("policy:*")
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis invalidate error: {e}")
        self.memory_cache.clear()
        logger.info("Policy cache successfully invalidated")


cache_service = PolicyCacheService()
