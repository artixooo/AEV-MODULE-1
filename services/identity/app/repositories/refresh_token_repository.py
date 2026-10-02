from datetime import datetime, timezone
import hashlib

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def create_refresh_token(
    db: Session,
    user_id,
    session_id,
    token: str,
    expires_at,
):
    token_hash = hash_refresh_token(token)

    refresh_token = RefreshToken(
        user_id=user_id,
        session_id=session_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(refresh_token)
    db.flush()
    db.refresh(refresh_token)

    return refresh_token


def get_refresh_token(
    db: Session,
    token: str,
):
    token_hash = hash_refresh_token(token)

    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash
        )
        .first()
    )


def is_refresh_token_valid(
    refresh_token: RefreshToken,
) -> bool:
    now = datetime.now(timezone.utc)

    expires_at = refresh_token.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    return (
        not refresh_token.revoked
        and expires_at > now
    )


def revoke_refresh_token(
    db: Session,
    refresh_token: RefreshToken,
):
    refresh_token.revoked = True
    refresh_token.revoked_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(refresh_token)

    return refresh_token

