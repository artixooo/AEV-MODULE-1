import redis
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.redis_client import get_redis
from app.db.session import get_db
from app.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
def health():
    """Returns 200 if the process is up. Does not check dependencies."""
    return HealthService.check_liveness()


@router.get("/ready", summary="Readiness probe")
def ready(
    response: Response,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
):
    """Returns 200 only if Postgres and Redis are reachable, else 503."""
    result = HealthService.check_readiness(db, redis_client)

    if result["status"] != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return result
