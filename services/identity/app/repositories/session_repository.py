from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session

from app.models.session import Session as SessionModel


def create_session(
    db: Session,
    user_id,
    tenant_id,
    expires_at,
):
    session = SessionModel(
        id=uuid.uuid4(),
        user_id=user_id,
        tenant_id=tenant_id,
        expires_at=expires_at,
    )

    db.add(session)
    db.flush()
    db.refresh(session)

    return session


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


def get_sessions_by_user(
    db: Session,
    user_id,
):
    return (
        db.query(SessionModel)
        .filter(
            SessionModel.user_id == user_id
        )
        .order_by(SessionModel.created_at.desc())
        .all()
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


def cleanup_expired_sessions(
    db: Session,
) -> int:
    """
    Mark expired active sessions inactive.

    Returns the number of sessions cleaned up.
    """
    now = datetime.now(timezone.utc)

    expired_sessions = (
        db.query(SessionModel)
        .filter(
            SessionModel.is_active.is_(True),
            SessionModel.expires_at <= now,
        )
        .all()
    )

    for session in expired_sessions:
        session.is_active = False

    db.flush()

    return len(expired_sessions)


def revoke_session(
    db: Session,
    session: SessionModel,
):
    session.is_active = False

    db.commit()
    db.refresh(session)

    return session


def revoke_sessions_by_user(
    db: Session,
    user_id,
):
    sessions = (
        db.query(SessionModel)
        .filter(
            SessionModel.user_id == user_id,
            SessionModel.is_active.is_(True),
        )
        .all()
    )

    for session in sessions:
        session.is_active = False

    db.flush()

    return sessions
