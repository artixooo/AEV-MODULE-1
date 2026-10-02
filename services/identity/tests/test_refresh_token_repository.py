from datetime import datetime, timedelta, timezone
import uuid

from app.models.user import User
from app.models.session import Session as SessionModel
from app.repositories.refresh_token_repository import (
    hash_refresh_token,
    create_refresh_token,
    get_refresh_token,
    is_refresh_token_valid,
    revoke_refresh_token,
)


TENANT_ID = uuid.UUID(
    "11111111-1111-1111-1111-111111111111"
)


def create_test_user(db_session):
    user = User(
        tenant_id=TENANT_ID,
        username=f"token_user_{uuid.uuid4().hex[:8]}",
        email=f"token_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="test-hash",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def create_test_session(db_session, user):
    session = SessionModel(
        id=uuid.uuid4(),
        user_id=user.id,
        tenant_id=user.tenant_id,
        session_token=uuid.uuid4().hex,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    return session


def test_refresh_token_hashing():
    token = "test-refresh-token"

    hashed = hash_refresh_token(token)

    assert hashed != token
    assert len(hashed) == 64
    assert hashed == hash_refresh_token(token)


def test_refresh_token_creation(db_session):
    user = create_test_user(db_session)
    session = create_test_session(db_session, user)

    token = "test-refresh-token-create"

    refresh_token = create_refresh_token(
        db=db_session,
        user_id=user.id,
        session_id=session.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    assert refresh_token is not None
    assert refresh_token.user_id == user.id
    assert refresh_token.session_id == session.id
    assert refresh_token.token_hash == hash_refresh_token(token)


def test_refresh_token_lookup(db_session):
    user = create_test_user(db_session)
    session = create_test_session(db_session, user)

    token = "test-refresh-token-lookup"

    create_refresh_token(
        db=db_session,
        user_id=user.id,
        session_id=session.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    result = get_refresh_token(
        db_session,
        token,
    )

    assert result is not None
    assert result.token_hash == hash_refresh_token(token)


def test_refresh_token_is_valid(db_session):
    user = create_test_user(db_session)
    session = create_test_session(db_session, user)

    refresh_token = create_refresh_token(
        db=db_session,
        user_id=user.id,
        session_id=session.id,
        token="test-refresh-token-valid",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    assert is_refresh_token_valid(refresh_token) is True


def test_expired_refresh_token_is_invalid(db_session):
    user = create_test_user(db_session)
    session = create_test_session(db_session, user)

    refresh_token = create_refresh_token(
        db=db_session,
        user_id=user.id,
        session_id=session.id,
        token="test-refresh-token-expired",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    assert is_refresh_token_valid(refresh_token) is False


def test_revoked_refresh_token_is_invalid(db_session):
    user = create_test_user(db_session)
    session = create_test_session(db_session, user)

    refresh_token = create_refresh_token(
        db=db_session,
        user_id=user.id,
        session_id=session.id,
        token="test-refresh-token-revoke",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    assert is_refresh_token_valid(refresh_token) is True

    revoke_refresh_token(
        db_session,
        refresh_token,
    )

    assert refresh_token.revoked is True
    assert is_refresh_token_valid(refresh_token) is False