import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


def hash_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def save_refresh_token(
    db: Session,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    token: str,
    expires_at: datetime
):
    refresh_token = RefreshToken(
        user_id=user_id,
        session_id=session_id,
        token_hash=hash_token(token),
        expires_at=expires_at
    )

    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return refresh_token


def get_refresh_token(
    db: Session,
    token: str
):
    token_hash = hash_token(token)

    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked.is_(False),
            RefreshToken.expires_at > datetime.now(timezone.utc)
        )
        .first()
    )


def revoke_refresh_token(
    db: Session,
    token: str
):
    stored_token = get_refresh_token(
        db,
        token
    )

    if not stored_token:
        return None

    stored_token.revoked = True
    stored_token.revoked_at = datetime.now(timezone.utc)

    db.commit()

    return stored_token