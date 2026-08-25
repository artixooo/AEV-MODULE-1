import os

from redis.asyncio import Redis


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")


redis_client = Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)


async def get_redis():
    return redis_client


async def close_redis():
    await redis_client.close()