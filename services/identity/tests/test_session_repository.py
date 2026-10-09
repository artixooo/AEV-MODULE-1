from datetime import datetime, timedelta, timezone
import uuid

from app.models.user import User
from app.repositories.session_repository import (
    create_session,
    get_session_by_id,
    is_session_valid,
    revoke_session,
)


TENANT_ID = uuid.UUID(
    "11111111-1111-1111-1111-111111111111"
)


def create_test_user(db_session):
    user = User(
        tenant_id=TENANT_ID,
        username=f"session_user_{uuid.uuid4().hex[:8]}",
        email=f"session_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="test-hash",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def test_session_creation(db_session):
    user = create_test_user(db_session)

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    session = create_session(
        db=db_session,
        user_id=user.id,
        tenant_id=user.tenant_id,
        expires_at=expires_at,
    )

    assert session is not None
    assert session.id is not None
    assert session.user_id == user.id
    assert session.tenant_id == user.tenant_id
    assert not hasattr(session, "session_token")
    assert session.is_active is True


def test_session_lookup_by_id(db_session):
    user = create_test_user(db_session)

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    session = create_session(
        db=db_session,
        user_id=user.id,
        tenant_id=user.tenant_id,
        expires_at=expires_at,
    )

    result = get_session_by_id(
        db_session,
        session.id,
    )

    assert result is not None
    assert result.id == session.id


def test_session_is_valid(db_session):
    user = create_test_user(db_session)

    session = create_session(
        db=db_session,
        user_id=user.id,
        tenant_id=user.tenant_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    assert is_session_valid(session) is True


def test_expired_session_is_invalid(db_session):
    user = create_test_user(db_session)

    session = create_session(
        db=db_session,
        user_id=user.id,
        tenant_id=user.tenant_id,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    assert is_session_valid(session) is False


def test_revoked_session_is_invalid(db_session):
    user = create_test_user(db_session)

    session = create_session(
        db=db_session,
        user_id=user.id,
        tenant_id=user.tenant_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    assert is_session_valid(session) is True

    revoke_session(
        db_session,
        session,
    )

    assert session.is_active is False
    assert is_session_valid(session) is False