import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repository import get_user_by_email
from app.repositories.session_repository import (
    create_session,
    get_session_by_id,
    is_session_valid,
)
from app.repositories.refresh_token_repository import (
    create_refresh_token,
    get_refresh_token,
    is_refresh_token_valid,
)
from app.utils.jwt import (
    create_access_token,
    create_refresh_token as create_jwt_refresh_token,
    decode_token,
)
from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        password_hash
    )


def login_user(
    db: Session,
    email: str,
    password: str,
):
    db_user = get_user_by_email(
        db,
        email,
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    if not verify_password(
        password,
        db_user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    if db_user.status != "ACTIVE":
        raise HTTPException(
            status_code=403,
            detail="User account is not active",
        )

    token_payload = {
        "sub": str(db_user.id),
        "email": db_user.email,
        "tenant_id": str(db_user.tenant_id),
    }

    access_token = create_access_token(
        token_payload
    )

    refresh_token = create_jwt_refresh_token(
        token_payload
    )

    session_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days=7)
    )

    session_token = secrets.token_urlsafe(32)

    try:
        user_session = create_session(
            db=db,
            user_id=db_user.id,
            tenant_id=db_user.tenant_id,
            session_token=session_token,
            expires_at=session_expires_at,
        )

        create_refresh_token(
            db=db,
            user_id=db_user.id,
            session_id=user_session.id,
            token=refresh_token,
            expires_at=session_expires_at,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(
    db: Session,
    refresh_token: str,
):
    stored_token = get_refresh_token(
        db,
        refresh_token,
    )

    if not stored_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    if not is_refresh_token_valid(
        stored_token,
    ):
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired or revoked",
        )

    session = get_session_by_id(
        db,
        stored_token.session_id,
    )

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Session not found",
        )

    if not is_session_valid(session):
        raise HTTPException(
            status_code=401,
            detail="Session expired or revoked",
        )

    payload = decode_token(
        refresh_token,
    )

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    email = payload.get("email")
    tenant_id = payload.get("tenant_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token payload",
        )

    new_access_token = create_access_token(
        {
            "sub": user_id,
            "email": email,
            "tenant_id": tenant_id,
        }
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
