from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.redis import check_redis, close_redis
from app.db.migrations import run_migrations

# Import models so SQLAlchemy registers them with Base
from app.models.user import User
from app.models.session import Session
from app.models.refresh_token import RefreshToken

from app.routers.auth_router import router as auth_router
from app.routers.router_logout import router as logout_router
from app.routers.router_sessions import router as sessions_router
from app.services.auth_service import AuthError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.

    Startup:
    - Run Identity Service database migrations
    - Check Redis connectivity

    Shutdown:
    - Close Redis connection
    """

    try:
        run_migrations()
        print("Database migrations completed successfully!")

    except Exception as e:
        print(f"Database migration failed: {e}")
        raise

    try:
        await check_redis()
        print("Redis connected successfully!")

    except Exception as e:
        print(f"Redis connection failed: {e}")

    yield

    await close_redis()
    print("Identity Service shutdown complete")



app = FastAPI(
    title="Identity Service",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(AuthError)
async def auth_error_handler(
    request: Request,
    exc: AuthError,
):
    return JSONResponse(
        status_code=401,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code,
        },
    )


app.include_router(auth_router)
app.include_router(logout_router)
app.include_router(sessions_router)


@app.get("/")
def root():
    return {
        "message": "Identity Service Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "identity"
    }


@app.get("/ready")
async def readiness():

    try:
        redis_status = await check_redis()

        if redis_status:
            return {
                "status": "ready",
                "database": "connected",
                "redis": "connected"
            }

    except Exception:
        pass

    return {
        "status": "not_ready",
        "database": "connected",
        "redis": "disconnected"
    }
