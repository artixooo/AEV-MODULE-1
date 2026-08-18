"""
Policy Service Main Application Entrypoint.

Squad 4 - Pod Alpha (Foundation & Identity)
Squad Lead: Utkarsh Pratham
Squad Member: Narayanan Varadarajan

Week 1 scope: project setup, config, DB models mirroring the
migration-defined schema, and health/readiness endpoints only.
RBAC/ABAC evaluation, SoD enforcement, permission endpoints, and
caching are Week 2 work and are intentionally not wired in here.

Note: this service does not create or seed its own database tables.
Schema is owned by database/policy/migrations/*.sql, applied via
database/scripts/migrate.sh, and seed data will live in
database/policy/seeds/seed_policy_data.sql, applied via
database/scripts/seed.sh. Keeping table creation/seeding out of the
app avoids the app silently drifting from the migration-defined schema.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import app.models.policy_models  # Ensure models are imported for metadata/relationship registration
from app.routers import health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Policy Service",
    description="Pod Alpha Authorization Service — Week 1 project setup & authorization database preparation",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router.router)


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "status": "running",
        "docs_url": "/docs"
    }
