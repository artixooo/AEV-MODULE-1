"""
services/identity/app/routers/router_logout.py

POST /api/v1/auth/logout
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.api_auth import (
    AuthErrorResponse,
    LogoutRequest,
    LogoutResponse,
)
from app.api.api_auth_deps import get_current_user_id
from app.core.database import get_db
from app.services.auth_service import (
    AuthError,
    revoke_refresh_token,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=200,
    responses={
        401: {
            "model": AuthErrorResponse,
            "description": "Authentication failed",
        }
    },
    summary="Revoke a refresh token, ending the session",
)
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> LogoutResponse:
    try:
        revoke_refresh_token(
            db=db,
            refresh_token=payload.refresh_token,
            requesting_user_id=user_id,
        )
    except AuthError as exc:
        return JSONResponse(
            status_code=401,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
            },
        )

    return LogoutResponse()
