from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import settings
from app.core.logging import logger
from app.routers.organization import router as organization_router
from app.routers.membership import router as membership_router
from app.routers.workspace import router as workspace_router
from app.routers.project import router as project_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("%s started", settings.APP_NAME)

    yield

    logger.info("%s stopped", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="Organization Service for Pod Alpha",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "status": "running",
        "version": "1.0.0"
    }


app.include_router(health_router)
app.include_router(organization_router)
app.include_router(membership_router)
app.include_router(workspace_router)
app.include_router(project_router)
