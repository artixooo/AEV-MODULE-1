from datetime import datetime, timedelta, timezone
import uuid

import pytest

from app.models.refresh_token import RefreshToken
from app.models.session import Session as SessionModel
from app.models.user import User
from app.api.api_auth_deps import get_current_user_id
from app.repositories.refresh_token_repository import hash_refresh_token
from app.services.auth_service import (
    TokenInvalidError,
    TokenOwnershipError,
    issue_token_pair,
    refresh,
    revoke_refresh_token,
)


TENANT_ID = uuid.UUID(
    "11111111-1111-1111-1111-111111111111"
)


def create_test_user(db_session, prefix="auth"):
    user = User(
        tenant_id=TENANT_ID,
        username=f"{prefix}_{uuid.uuid4().hex[:8]}",
        email=f"{prefix}_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="test-hash",
        status="ACTIVE",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def test_issue_token_pair_creates_session_and_refresh_token(db_session):
    user = create_test_user(db_session, "issue")

    access_token, refresh_token = issue_token_pair(
        db=db_session,
        user=user,
    )

    assert access_token
    assert refresh_token

    session = (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == user.id)
        .first()
    )

    assert session is not None
    assert session.user_id == user.id
    assert session.tenant_id == user.tenant_id
    assert not hasattr(session, "session_token")
    assert session.is_active is True

    stored_token = (
        db_session.query(RefreshToken)
        .filter(RefreshToken.session_id == session.id)
        .first()
    )

    assert stored_token is not None
    assert stored_token.user_id == user.id
    assert stored_token.session_id == session.id
    assert stored_token.revoked is False
    assert stored_token.token_hash == hash_refresh_token(refresh_token)
    assert stored_token.token_hash != refresh_token


def test_refresh_rotates_token_and_keeps_same_session(db_session):
    user = create_test_user(db_session, "rotate")

    _, old_refresh_token = issue_token_pair(
        db=db_session,
        user=user,
    )

    old_stored_token = (
        db_session.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked.is_(False),
        )
        .first()
    )

    session = (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == user.id)
        .first()
    )

    assert old_stored_token is not None
    assert session is not None

    old_session_id = session.id
    old_token_id = old_stored_token.id

    result = refresh(
        db=db_session,
        refresh_token=old_refresh_token,
    )

    assert result["access_token"]
    assert result["refresh_token"]
    assert result["refresh_token"] != old_refresh_token

    db_session.expire_all()

    old_token = (
        db_session.query(RefreshToken)
        .filter(RefreshToken.id == old_token_id)
        .first()
    )

    new_token = (
        db_session.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked.is_(False),
        )
        .first()
    )

    current_session = (
        db_session.query(SessionModel)
        .filter(SessionModel.id == old_session_id)
        .first()
    )

    assert old_token is not None
    assert old_token.revoked is True

    assert new_token is not None
    assert new_token.id != old_token.id
    assert new_token.session_id == old_session_id

    assert current_session is not None
    assert current_session.is_active is True


def test_old_refresh_token_cannot_be_reused_after_rotation(db_session):
    user = create_test_user(db_session, "reuse")

    _, old_refresh_token = issue_token_pair(
        db=db_session,
        user=user,
    )

    refresh(
        db=db_session,
        refresh_token=old_refresh_token,
    )

    with pytest.raises(TokenInvalidError) as exc_info:
        refresh(
            db=db_session,
            refresh_token=old_refresh_token,
        )

    assert exc_info.value.error_code == "INVALID_REFRESH_TOKEN"


def test_logout_revokes_refresh_token_and_session(db_session):
    user = create_test_user(db_session, "logout")

    _, refresh_token = issue_token_pair(
        db=db_session,
        user=user,
    )

    stored_token = (
        db_session.query(RefreshToken)
        .filter(RefreshToken.user_id == user.id)
        .first()
    )

    session = (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == user.id)
        .first()
    )

    assert stored_token is not None
    assert session is not None

    revoke_refresh_token(
        db=db_session,
        refresh_token=refresh_token,
        requesting_user_id=str(user.id),
    )

    db_session.expire_all()

    revoked_token = (
        db_session.query(RefreshToken)
        .filter(RefreshToken.id == stored_token.id)
        .first()
    )

    revoked_session = (
        db_session.query(SessionModel)
        .filter(SessionModel.id == session.id)
        .first()
    )

    assert revoked_token is not None
    assert revoked_token.revoked is True

    assert revoked_session is not None
    assert revoked_session.is_active is False


def test_revoked_session_cannot_refresh(db_session):
    user = create_test_user(db_session, "revoked")

    _, refresh_token = issue_token_pair(
        db=db_session,
        user=user,
    )

    session = (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == user.id)
        .first()
    )

    assert session is not None

    session.is_active = False
    db_session.commit()

    with pytest.raises(TokenInvalidError) as exc_info:
        refresh(
            db=db_session,
            refresh_token=refresh_token,
        )

    assert exc_info.value.error_code == "INVALID_SESSION"


def test_refresh_token_ownership_is_enforced(db_session):
    owner = create_test_user(db_session, "owner")
    other_user = create_test_user(db_session, "other")

    _, refresh_token = issue_token_pair(
        db=db_session,
        user=owner,
    )

    with pytest.raises(TokenOwnershipError) as exc_info:
        revoke_refresh_token(
            db=db_session,
            refresh_token=refresh_token,
            requesting_user_id=str(other_user.id),
        )

    assert exc_info.value.error_code == "TOKEN_OWNERSHIP_ERROR"

    stored_token = (
        db_session.query(RefreshToken)
        .filter(RefreshToken.user_id == owner.id)
        .first()
    )

    session = (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == owner.id)
        .first()
    )

    assert stored_token is not None
    assert stored_token.revoked is False

    assert session is not None
    assert session.is_active is True

def test_access_token_accepts_active_session(db_session):
    user = create_test_user(db_session, "access_active")

    access_token, _ = issue_token_pair(
        db=db_session,
        user=user,
    )

    authenticated_user_id = get_current_user_id(
        token=access_token,
        db=db_session,
    )

    assert authenticated_user_id == str(user.id)


def test_access_token_rejects_revoked_session(db_session):
    user = create_test_user(db_session, "access_revoked")

    access_token, _ = issue_token_pair(
        db=db_session,
        user=user,
    )

    session = (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == user.id)
        .first()
    )

    assert session is not None

    session.is_active = False
    db_session.commit()

    with pytest.raises(TokenInvalidError) as exc_info:
        get_current_user_id(
            token=access_token,
            db=db_session,
        )

    assert exc_info.value.error_code == "INVALID_SESSION"


def test_access_token_rejects_expired_session(db_session):
    user = create_test_user(db_session, "access_expired")

    access_token, _ = issue_token_pair(
        db=db_session,
        user=user,
    )

    session = (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == user.id)
        .first()
    )

    assert session is not None

    session.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    with pytest.raises(TokenInvalidError) as exc_info:
        get_current_user_id(
            token=access_token,
            db=db_session,
        )

    assert exc_info.value.error_code == "INVALID_SESSION"


def test_access_token_rejects_session_ownership_mismatch(db_session):
    owner = create_test_user(db_session, "access_owner")
    other_user = create_test_user(db_session, "access_other")

    access_token, _ = issue_token_pair(
        db=db_session,
        user=owner,
    )

    session = (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == owner.id)
        .first()
    )

    assert session is not None

    session.user_id = other_user.id
    db_session.commit()

    with pytest.raises(TokenInvalidError) as exc_info:
        get_current_user_id(
            token=access_token,
            db=db_session,
        )

    assert exc_info.value.error_code == "INVALID_SESSION"


def test_access_token_rejects_session_tenant_mismatch(db_session):
    user = create_test_user(db_session, "access_tenant")

    access_token, _ = issue_token_pair(
        db=db_session,
        user=user,
    )

    session = (
        db_session.query(SessionModel)
        .filter(SessionModel.user_id == user.id)
        .first()
    )

    assert session is not None

    session.tenant_id = uuid.UUID(
        "22222222-2222-2222-2222-222222222222"
    )
    db_session.commit()

    with pytest.raises(TokenInvalidError) as exc_info:
        get_current_user_id(
            token=access_token,
            db=db_session,
        )

    assert exc_info.value.error_code == "INVALID_SESSION"
