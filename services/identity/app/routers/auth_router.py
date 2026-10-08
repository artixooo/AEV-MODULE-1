import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.api_auth import (
    AuthErrorResponse,
    LoginRequest,
    RefreshRequest,
    RefreshResponse,
    TokenResponse,
)
from app.api.api_auth_deps import get_current_user_id
from app.core.database import get_db
from app.repositories.user_repository import (
    get_user_by_email,
    get_user_by_id,
)
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.auth_service import (
    AuthError,
    TokenInvalidError,
    login as authenticate_and_login,
    refresh as refresh_tokens,
)
from app.services.user_service import create_user


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user: UserCreate,
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    existing_user = get_user_by_email(
        db,
        user.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    return create_user(
        db,
        user,
        tenant_id,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {
            "model": AuthErrorResponse,
            "description": "Authentication failed",
        }
    },
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        return authenticate_and_login(
            db=db,
            email=payload.email,
            password=payload.password,
        )
    except AuthError as exc:
        return JSONResponse(
            status_code=401,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
            },
        )


@router.get("/profile")
def profile(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(
        db,
        user_id,
    )

    return {
        "message": "JWT verification successful",
        "user_id": user_id,
        "email": user.email if user else None,
        "tenant_id": str(user.tenant_id) if user else None,
    }


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    responses={
        401: {
            "model": AuthErrorResponse,
            "description": "Refresh token validation failed",
        }
    },
)
def refresh(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
):
    try:
        return refresh_tokens(
            db=db,
            refresh_token=payload.refresh_token,
        )
    except (TokenInvalidError, AuthError) as exc:
        return JSONResponse(
            status_code=401,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
            },
        )
