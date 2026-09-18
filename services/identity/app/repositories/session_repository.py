from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session

from app.models.session import Session as SessionModel


def create_session(
    db: Session,
    user_id,
    tenant_id,
    session_token: str,
    expires_at,
):
    session = SessionModel(
        id=uuid.uuid4(),
        user_id=user_id,
        tenant_id=tenant_id,
        session_token=session_token,
        expires_at=expires_at,
    )

    db.add(session)
    db.flush()
    db.refresh(session)

    return session


def get_session_by_token(
    db: Session,
    session_token: str,
):
    return (
        db.query(SessionModel)
        .filter(
            SessionModel.session_token == session_token
        )
        .first()
    )


def get_session_by_id(
    db: Session,
    session_id,
):
    return (
        db.query(SessionModel)
        .filter(
            SessionModel.id == session_id
        )
        .first()
    )


def is_session_valid(
    session: SessionModel,
) -> bool:
    now = datetime.now(timezone.utc)

    expires_at = session.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    return (
        session.is_active
        and expires_at > now
    )


def revoke_session(
    db: Session,
    session: SessionModel,
):
    session.is_active = False

    db.commit()
    db.refresh(session)

    return session