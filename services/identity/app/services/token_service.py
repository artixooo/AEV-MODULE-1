from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.refresh_token_repository import (
    create_refresh_token,
    get_refresh_token,
    is_refresh_token_valid,
    revoke_refresh_token,
)


def save_refresh_token(
    db: Session,
    user_id,
    session_id,
    token: str,
    expires_at: datetime,
):
    return create_refresh_token(
        db=db,
        user_id=user_id,
        session_id=session_id,
        token=token,
        expires_at=expires_at,
    )


def get_refresh_token_by_token(
    db: Session,
    token: str,
):
    refresh_token = get_refresh_token(
        db=db,
        token=token,
    )

    if not refresh_token:
        return None

    if not is_refresh_token_valid(refresh_token):
        return None

    return refresh_token


def revoke_refresh_token_by_token(
    db: Session,
    token: str,
):
    refresh_token = get_refresh_token_by_token(
        db=db,
        token=token,
    )

    if not refresh_token:
        return None

    return revoke_refresh_token(
        db=db,
        refresh_token=refresh_token,
    )
