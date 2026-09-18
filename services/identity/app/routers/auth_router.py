import uuid

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user_schema import (
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.user_service import create_user
from app.repositories.user_repository import get_user_by_email
from app.services.auth_service import (
    login_user,
    refresh_access_token,
)
from app.utils.jwt import verify_token


router = APIRouter(
    prefix="/auth",
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


@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    return login_user(
        db=db,
        email=user.email,
        password=user.password,
    )


@router.get("/profile")
def profile(
    payload: dict = Depends(verify_token),
):
    return {
        "message": "JWT verification successful",
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "tenant_id": payload.get("tenant_id"),
    }


@router.post("/refresh")
def refresh(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    return refresh_access_token(
        db=db,
        refresh_token=refresh_token,
    )
