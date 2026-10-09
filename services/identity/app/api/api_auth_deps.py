import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.session_repository import (
    get_session_by_id,
    is_session_valid,
)
from app.services.auth_service import (
    TokenInvalidError,
    decode_access_token,
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> str:
    payload = decode_access_token(token)

    user_id = payload.get("sub")
    session_id = payload.get("sid")
    tenant_id = payload.get("tenant_id")

    if not user_id:
        raise TokenInvalidError(
            detail="Token payload is missing the subject (sub) claim",
            error_code="INVALID_TOKEN_PAYLOAD",
        )

    if not session_id:
        raise TokenInvalidError(
            detail="Access token payload is missing the session identifier",
            error_code="INVALID_TOKEN_PAYLOAD",
        )

    if not tenant_id:
        raise TokenInvalidError(
            detail="Access token payload is missing the tenant identifier",
            error_code="INVALID_TOKEN_PAYLOAD",
        )

    try:
        session_uuid = uuid.UUID(str(session_id))
    except ValueError:
        raise TokenInvalidError(
            detail="Access token contains an invalid session identifier",
            error_code="INVALID_TOKEN_PAYLOAD",
        )

    session = get_session_by_id(
        db=db,
        session_id=session_uuid,
    )

    if not session:
        raise TokenInvalidError(
            detail="Session associated with access token was not found",
            error_code="INVALID_SESSION",
        )

    if str(session.user_id) != str(user_id):
        raise TokenInvalidError(
            detail="Access token session ownership validation failed",
            error_code="INVALID_SESSION",
        )

    if str(session.tenant_id) != str(tenant_id):
        raise TokenInvalidError(
            detail="Access token session tenant validation failed",
            error_code="INVALID_SESSION",
        )

    if not is_session_valid(session):
        raise TokenInvalidError(
            detail="Session is inactive or expired",
            error_code="INVALID_SESSION",
        )

    return str(user_id)
