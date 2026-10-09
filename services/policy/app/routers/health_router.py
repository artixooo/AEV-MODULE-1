"""
Health & Readiness Endpoints for Policy Service.

GET /health  — Liveness probe. Returns 200 immediately; no I/O performed.
              Used by Docker / Kubernetes to know whether the process is alive.

GET /ready   — Readiness probe. Checks PostgreSQL connectivity.
              Returns 200 when fully ready, 503 when the database is
              unhealthy so the load-balancer can remove the instance.

Author: Pod Alpha Security Engineering
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

import time
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])

_START_TIME: float = time.monotonic()


@router.get(
    "/health",
    summary="Liveness probe",
    description="Returns 200 immediately. No I/O. Used to confirm the process is alive.",
)
def health_check():
    uptime_seconds = round(time.monotonic() - _START_TIME, 1)
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/ready",
    summary="Readiness probe",
    description=(
        "Checks PostgreSQL connectivity. "
        "Returns 200 when ready, 503 when the database is unreachable."
    ),
)
def readiness_check(response: Response, db: Session = Depends(get_db)):
    checks = {}
    overall_healthy = True

    try:
        db.execute(text("SELECT 1"))
        checks["database"] = {"status": "connected", "type": "postgresql"}
    except Exception as exc:
        logger.warning(f"Readiness check — database unhealthy: {exc}")
        checks["database"] = {"status": "unhealthy", "error": str(exc), "type": "postgresql"}
        overall_healthy = False

    if not overall_healthy:
        response.status_code = 503

    return {
        "status": "ready" if overall_healthy else "unhealthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
