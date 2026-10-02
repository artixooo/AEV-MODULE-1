"""
Authentication business logic for the Identity Service.

Responsibilities:
- Password hashing and verification
- User authentication
- JWT access/refresh token creation and validation
- Refresh-token persistence/revocation coordination
- Authentication error definitions

FastAPI dependency injection MUST NOT be used in this service layer.
Database/session dependencies are supplied by the router layer.
"""
from datetime import datetime, timedelta, timezone
from typing import Any
import uuid

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.refresh_token import RefreshToken
from app.models.session import Session as UserSession
from app.models.user import User
from app.schemas.user_schema import UserCreate

from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

from app.repositories.refresh_token_repository import (
    get_refresh_token,
    create_refresh_token as persist_refresh_token,
    revoke_refresh_token as persist_revoke_refresh_token,
    is_refresh_token_valid,
)

from app.repositories.session_repository import (
    get_session_by_id,
    is_session_valid,
    revoke_session,
)

# ============================================================================
# Password hashing
# ============================================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    """Verify a plaintext password against its stored hash."""
    return pwd_context.verify(
        plain_password,
        password_hash,
    )


# ============================================================================
# Authentication exceptions
# ============================================================================


class AuthError(Exception):
    """
    Base authentication error.

    The router can convert this into the API's standard:
        {"detail": "...", "error_code": "..."}
    response.
    """

    def __init__(
        self,
        detail: str,
        error_code: str = "AUTHENTICATION_ERROR",
    ):
        self.detail = detail
        self.error_code = error_code
        super().__init__(detail)


class TokenInvalidError(AuthError):
    """Raised when a JWT is invalid, expired, or malformed."""

    def __init__(
        self,
        detail: str = "Invalid or expired access token",
        error_code: str = "INVALID_TOKEN",
    ):
        super().__init__(
            detail=detail,
            error_code=error_code,
        )


class TokenOwnershipError(AuthError):
    """Raised when a user attempts to revoke another user's token."""

    def __init__(
        self,
        detail: str = "Refresh token does not belong to the authenticated user",
        error_code: str = "TOKEN_OWNERSHIP_ERROR",
    ):
        super().__init__(
            detail=detail,
            error_code=error_code,
        )


# ============================================================================
# JWT validation
# ============================================================================


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate an access token.

    The actual JWT decoding is delegated to the canonical implementation
    in app.utils.jwt. This function only adds access-token-specific
    validation required by the authentication dependency.
    """

    payload = decode_token(token)

    if not payload:
        raise TokenInvalidError(
            detail="Invalid or expired access token",
            error_code="INVALID_TOKEN",
        )

    if payload.get("type") != "access":
        raise TokenInvalidError(
            detail="Invalid token type",
            error_code="INVALID_TOKEN_TYPE",
        )

    if not payload.get("sub"):
        raise TokenInvalidError(
            detail="Token payload is missing the subject (sub) claim",
            error_code="INVALID_TOKEN_PAYLOAD",
        )

    return payload


def decode_refresh_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a refresh token.

    JWT decoding remains centralized in app.utils.jwt.
    """

    payload = decode_token(token)

    if not payload:
        raise TokenInvalidError(
            detail="Invalid or expired refresh token",
            error_code="INVALID_REFRESH_TOKEN",
        )

    if payload.get("type") != "refresh":
        raise TokenInvalidError(
            detail="Invalid token type",
            error_code="INVALID_TOKEN_TYPE",
        )

    if not payload.get("sub"):
        raise TokenInvalidError(
            detail="Refresh token payload is missing the subject (sub) claim",
            error_code="INVALID_TOKEN_PAYLOAD",
        )

    return payload


# ============================================================================
# User authentication
# ============================================================================


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    """
    Authenticate a user using email and password.

    Raises AuthError instead of returning FastAPI HTTPException so that
    the service layer remains independent of FastAPI.
    """

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise AuthError(
            detail="Invalid email or password",
            error_code="INVALID_CREDENTIALS",
        )

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise AuthError(
            detail="Invalid email or password",
            error_code="INVALID_CREDENTIALS",
        )

    if user.status != "ACTIVE":
        raise AuthError(
            detail="User account is not active",
            error_code="USER_INACTIVE",
        )

    return user


# ============================================================================
# User registration
# ============================================================================


def register_user(
    db: Session,
    user_in: UserCreate,
    tenant_id: uuid.UUID,
) -> User:
    """
    Register a new user.

    This function intentionally does not use FastAPI Depends.
    """

    existing_user = (
        db.query(User)
        .filter(User.email == user_in.email)
        .first()
    )

    if existing_user:
        raise AuthError(
            detail="Email already registered",
            error_code="EMAIL_ALREADY_REGISTERED",
        )

    password_hash = hash_password(
        user_in.password
    )

    new_user = User(
        tenant_id=tenant_id,
        username=user_in.username,
        email=user_in.email,
        password_hash=password_hash,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ============================================================================
# Token issuance
# ============================================================================


def issue_access_token(
    user: User,
) -> str:
    """Create an access token for a user."""

    return create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "tenant_id": str(user.tenant_id),
        }
    )


def issue_token_pair(
    db: Session,
    user: User,
) -> tuple[str, str]:
    """
    Create an access/refresh token pair and persist the refresh token
    in PostgreSQL.
    """

    access_token = issue_access_token(user)

    refresh_token = create_refresh_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "tenant_id": str(user.tenant_id),
        }
    )

    refresh_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days=7)
    )

    user_session = UserSession(
        user_id=user.id,
        tenant_id=user.tenant_id,
        session_token=refresh_token,
        expires_at=refresh_expires_at,
    )

    db.add(user_session)
    db.flush()


    persist_refresh_token(
        db=db,
        user_id=user.id,
        session_id=user_session.id,
        token=refresh_token,
        expires_at=refresh_expires_at,
    )
    db.commit()
    db.refresh(user_session)

    return access_token, refresh_token


# ============================================================================
# Login
# ============================================================================


def login(
    db: Session,
    email: str,
    password: str,
) -> dict[str, Any]:
    """
    Authenticate a user and issue an access/refresh token pair.
    """

    user = authenticate_user(
        db=db,
        email=email,
        password=password,
    )

    access_token, refresh_token = issue_token_pair(
        db=db,
        user=user,
    )

    return  {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "token_type": "bearer",
    "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

# ============================================================================
# Refresh access token
# ============================================================================
def refresh(
    db: Session,
    refresh_token: str,
) -> dict[str, Any]:
    """
    Validate and rotate a refresh token.

    The supplied refresh token must:
    - exist in PostgreSQL
    - not be revoked
    - not be expired
    - contain a valid JWT payload
    - belong to an active user

    The old refresh token is revoked and a new refresh token
    is persisted before returning the new token pair.
    """

    stored_token = get_refresh_token(
        db=db,
        token=refresh_token,
    )

    if not stored_token:
        raise TokenInvalidError(
            detail="Invalid or expired refresh token",
            error_code="INVALID_REFRESH_TOKEN",
        )

    if not is_refresh_token_valid(stored_token):
        raise TokenInvalidError(
            detail="Invalid or expired refresh token",
            error_code="INVALID_REFRESH_TOKEN",
        )

    payload = decode_refresh_token(refresh_token)

    user_id = payload.get("sub")

    if not user_id:
        raise TokenInvalidError(
            detail="Refresh token payload is missing the subject (sub) claim",
            error_code="INVALID_TOKEN_PAYLOAD",
        )

    session = get_session_by_id(
        db=db,
        session_id=stored_token.session_id,
    )

    if not session:
        raise TokenInvalidError(
            detail="Session associated with refresh token was not found",
            error_code="INVALID_SESSION",
        )

    if str(session.user_id) != str(user_id):
        raise TokenInvalidError(
            detail="Session ownership validation failed",
            error_code="INVALID_SESSION",
        )

    tenant_id = payload.get("tenant_id")

    if not tenant_id or str(session.tenant_id) != str(tenant_id):
        raise TokenInvalidError(
            detail="Session tenant validation failed",
            error_code="INVALID_SESSION",
        )

    if not is_session_valid(session):
        raise TokenInvalidError(
            detail="Session is inactive or expired",
            error_code="INVALID_SESSION",
        )

    if str(stored_token.user_id) != str(user_id):
        raise TokenInvalidError(
            detail="Refresh token ownership validation failed",
            error_code="INVALID_REFRESH_TOKEN",
        )

    try:
        user_uuid = uuid.UUID(str(user_id))
    except ValueError:
        raise TokenInvalidError(
            detail="Refresh token contains an invalid user identifier",
            error_code="INVALID_TOKEN_PAYLOAD",
        )

    user = (
        db.query(User)
        .filter(User.id == user_uuid)
        .first()
    )

    if not user:
        raise TokenInvalidError(
            detail="User associated with refresh token was not found",
            error_code="USER_NOT_FOUND",
        )

    if user.status != "ACTIVE":
        raise AuthError(
            detail="User account is not active",
            error_code="USER_INACTIVE",
        )

    # Update session activity before rotating the refresh token.
    session.last_activity = datetime.now(timezone.utc)
    db.flush()

    # Revoke the old refresh token.
    persist_revoke_refresh_token(
        db=db,
        refresh_token=stored_token,
    )

    # Issue a new access token.
    new_access_token = issue_access_token(
        user
    )

    # Issue a new refresh token.
    new_refresh_token = create_refresh_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "tenant_id": str(user.tenant_id),
        }
    )

    new_refresh_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days=7)
    )

    # Persist the new refresh token in PostgreSQL.
    persist_refresh_token(
        db=db,
        user_id=user.id,
        session_id=stored_token.session_id,
        token=new_refresh_token,
        expires_at=new_refresh_expires_at,
    )
    # Commit the new refresh-token record.
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }



# ============================================================================
# Refresh-token revocation / logout
# ============================================================================


def revoke_refresh_token(
    db: Session,
    refresh_token: str,
    requesting_user_id: str,
) -> RefreshToken:
    """
    Revoke a refresh token after validating token ownership.

    PostgreSQL refresh_tokens table.
    """

    payload = decode_refresh_token(
        refresh_token
    )

    token_owner_id = payload.get("sub")

    if not token_owner_id:
        raise TokenInvalidError(
            detail="Refresh token payload is missing the subject (sub) claim",
            error_code="INVALID_TOKEN_PAYLOAD",
        )

    if str(token_owner_id) != str(requesting_user_id):
        raise TokenOwnershipError()

    stored_token = get_refresh_token(
        db=db,
        token=refresh_token,
    )

    if not stored_token:
        raise TokenInvalidError(
            detail="Invalid, expired, or already revoked refresh token",
            error_code="INVALID_REFRESH_TOKEN",
        )

    if str(stored_token.user_id) != str(requesting_user_id):
        raise TokenOwnershipError()

    session = get_session_by_id(
        db=db,
        session_id=stored_token.session_id,
    )

    if not session:
        raise TokenInvalidError(
            detail="Session associated with refresh token was not found",
            error_code="INVALID_SESSION",
        )

    if str(session.user_id) != str(requesting_user_id):
        raise TokenOwnershipError()

    revoked_token = persist_revoke_refresh_token(
        db=db,
        refresh_token=stored_token,
    )

    if not revoked_token:
        raise TokenInvalidError(
            detail="Invalid, expired, or already revoked refresh token",
            error_code="INVALID_REFRESH_TOKEN",
        )

    revoke_session(
        db=db,
        session=session,
    )

    return revoked_token
