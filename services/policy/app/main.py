"""
Policy Service Main Application Entrypoint.

Squad 4 - Pod Alpha (Foundation & Identity)
Squad Lead: Utkarsh Pratham
Squad Member: Narayanan Varadarajan

Scope: project setup, config, DB models mirroring the migration-defined
schema, health/readiness endpoints, infra readiness (config loading,
graceful shutdown — Week 1/2), and the RBAC foundation (Issue #61) —
role/permission listing and a pure RBAC /evaluate endpoint, protected
by JWT authentication. ABAC evaluation, Segregation of Duties
enforcement, and caching are out of scope and are intentionally not
wired in here.

Schema ownership: Database tables are created and versioned exclusively through
the migration files in database/policy/migrations/*.sql, applied via
database/scripts/migrate.sh. Seed data lives in
database/policy/seeds/seed_policy_data.sql, applied via database/scripts/seed.sh.

Keeping table creation / seeding out of the application startup avoids the
service silently drifting from the migration-defined schema and makes it safe to
run multiple replicas without race conditions on table creation.
"""

import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
import app.models.policy_models  # noqa: F401 — import registers ORM metadata & relationships
from app.routers import health_router, policy_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — startup & graceful shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup:
        • Logs configuration summary (no sensitive values).
        • Verifies the database connection pool is reachable.

    Shutdown (yields back):
        • Disposes the SQLAlchemy connection pool so all in-flight queries
          complete and connections are returned cleanly.
    """
    # ---- STARTUP --------------------------------------------------------
    logger.info("=" * 60)
    logger.info("Policy Service starting up")
    logger.info(f"  APP_NAME : {settings.APP_NAME}")
    logger.info(f"  APP_ENV  : {settings.APP_ENV}")
    logger.info(f"  HOST     : {settings.HOST}:{settings.PORT}")
    logger.info(f"  DB host  : {_redact_url(settings.DATABASE_URL)}")
    logger.info("=" * 60)

    # Verify PostgreSQL connectivity
    from app.core.database import engine
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified successfully.")
    except Exception as exc:
        logger.error(f"Database connectivity check failed: {exc}")
        # In production, refuse to start if the DB is unreachable.
        if settings.APP_ENV != "development":
            logger.critical("Aborting startup — database is unreachable in non-development mode.")
            sys.exit(1)

    logger.info("Policy Service is ready to accept requests.")

    yield  # --- application runs here ---

    # ---- SHUTDOWN -------------------------------------------------------
    logger.info("Policy Service shutting down — disposing database connection pool …")
    from app.core.database import engine
    engine.dispose()
    logger.info("Policy Service shutdown complete.")


def _redact_url(url: str) -> str:
    """Return URL with password replaced by ***."""
    try:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        if parsed.password:
            netloc = parsed.netloc.replace(f":{parsed.password}@", ":***@")
            return urlunparse(parsed._replace(netloc=netloc))
    except Exception:
        pass
    return url


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Policy Service",
    description="Pod Alpha Authorization Service — infrastructure readiness & RBAC foundation",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router.router)
app.include_router(policy_router.router)


@app.get("/", tags=["Root"])
def root():
    """Service discovery / sanity-check endpoint."""
    return {
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "status": "running",
        "docs_url": "/docs",
        "health_url": "/health",
        "ready_url": "/ready",
    }


# ---------------------------------------------------------------------------
# Direct entrypoint (python -m app.main)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.APP_ENV == "development",
        log_level="info",
    )