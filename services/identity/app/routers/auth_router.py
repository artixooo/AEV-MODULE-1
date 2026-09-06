import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.session import Session as UserSession

from app.schemas.user_schema import (
    UserCreate,
    UserLogin,
    UserResponse
)

from app.services.user_service import (
    create_user,
    get_user_by_email
)

from app.services.auth_service import (
    verify_password
)

from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token
)

from app.services.token_service import (
    get_refresh_token,
    save_refresh_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================
# Register User
# ==========================

@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    tenant_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    existing_user = get_user_by_email(
        db,
        user.email
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return create_user(
        db,
        user,
        tenant_id
    )


# ==========================
# Login User
# ==========================

@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    db_user = get_user_by_email(
        db,
        user.email
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        user.password,
        db_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if db_user.status != "ACTIVE":
        raise HTTPException(
            status_code=403,
            detail="User account is not active"
        )

    access_token = create_access_token(
        {
            "sub": str(db_user.id),
            "email": db_user.email,
            "tenant_id": str(db_user.tenant_id)
        }
    )

    refresh_token = create_refresh_token(
        {
            "sub": str(db_user.id),
            "email": db_user.email,
            "tenant_id": str(db_user.tenant_id)
        }
    )

    session_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days=7)
    )

    user_session = UserSession(
        user_id=db_user.id,
        tenant_id=db_user.tenant_id,
        session_token=refresh_token,
        expires_at=session_expires_at
    )

    db.add(user_session)
    db.commit()
    db.refresh(user_session)

    save_refresh_token(
        db,
        db_user.id,
        user_session.id,
        refresh_token,
        session_expires_at
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ==========================
# Protected Profile API
# ==========================

@router.get("/profile")
def profile(
    payload: dict = Depends(verify_token)
):
    return {
        "message": "JWT verification successful",
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "tenant_id": payload.get("tenant_id")
    }


# ==========================
# Refresh Access Token
# ==========================

@router.post("/refresh")
def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    stored_token = get_refresh_token(
        db,
        refresh_token
    )

    if not stored_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )

    payload = decode_token(
        refresh_token
    )

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )

    user_id = payload.get("sub")
    email = payload.get("email")
    tenant_id = payload.get("tenant_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token payload"
        )

    new_access_token = create_access_token(
        {
            "sub": user_id,
            "email": email,
            "tenant_id": tenant_id
        }
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }