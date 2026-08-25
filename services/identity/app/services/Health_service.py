
import asyncio
import logging
from typing import Tuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

DB_TIMEOUT_SECONDS = 2.0
REDIS_TIMEOUT_SECONDS = 2.0


def get_health_status() -> dict:
    return {"status": "healthy"}


async def check_postgres(session: AsyncSession) -> Tuple[bool, str]:
    try:
        await asyncio.wait_for(session.execute(text("SELECT 1")), timeout=DB_TIMEOUT_SECONDS)
        return True, "ok"
    except asyncio.TimeoutError:
        logger.warning("Postgres readiness check timed out")
        return False, "timeout"
    except Exception as exc:
        logger.warning(f"Postgres readiness check failed: {exc}")
        return False, str(exc)


async def check_redis(redis_client: aioredis.Redis) -> Tuple[bool, str]:
    try:
        pong = await asyncio.wait_for(redis_client.ping(), timeout=REDIS_TIMEOUT_SECONDS)
        return (True, "ok") if pong else (False, "no pong")
    except asyncio.TimeoutError:
        logger.warning("Redis readiness check timed out")
        return False, "timeout"
    except Exception as exc:
        logger.warning(f"Redis readiness check failed: {exc}")
        return False, str(exc)


async def get_readiness_status(session: AsyncSession, redis_client: aioredis.Redis) -> Tuple[dict, bool]:
    db_ok, db_detail = await check_postgres(session)
    redis_ok, redis_detail = await check_redis(redis_client)
    overall_ok = db_ok and redis_ok
    body = {
        "status": "ready" if overall_ok else "not_ready",
        "checks": {
            "postgres": {"ok": db_ok, "detail": db_detail},
            "redis": {"ok": redis_ok, "detail": redis_detail},
        },
    }
    return body, overall_ok
