import redis.asyncio as redis

from app.core.config import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)


async def check_redis():
    return await redis_client.ping()


async def close_redis():
    await redis_client.close()