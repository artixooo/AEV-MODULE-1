import logging
import time

import redis
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class HealthService:
    """
    Infrastructure health/readiness checks only.
    Week 2 scope: no auth, no JWT, no OAuth/OIDC, no MFA, no password logic here.
    """

    @staticmethod
    def check_liveness() -> dict:
        return {"status": "ok"}

    @staticmethod
    def check_postgres(db: Session) -> dict:
        start = time.monotonic()
        try:
            db.execute(text("SELECT 1"))
            latency_ms = round((time.monotonic() - start) * 1000, 2)
            return {"status": "ok", "latency_ms": latency_ms}
        except SQLAlchemyError as exc:
            logger.error("Postgres readiness check failed: %s", exc)
            return {"status": "error", "detail": str(exc)}

    @staticmethod
    def check_redis(client: redis.Redis) -> dict:
        start = time.monotonic()
        try:
            client.ping()
            latency_ms = round((time.monotonic() - start) * 1000, 2)
            return {"status": "ok", "latency_ms": latency_ms}
        except redis.RedisError as exc:
            logger.error("Redis readiness check failed: %s", exc)
            return {"status": "error", "detail": str(exc)}

    @classmethod
    def check_readiness(cls, db: Session, redis_client: redis.Redis) -> dict:
        postgres_result = cls.check_postgres(db)
        redis_result = cls.check_redis(redis_client)

        checks = {"postgres": postgres_result, "redis": redis_result}
        overall_ok = all(check["status"] == "ok" for check in checks.values())

        return {
            "status": "ok" if overall_ok else "unavailable",
            "checks": checks,
        }
