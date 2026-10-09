from datetime import datetime, timedelta, timezone
import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db, SessionLocal
from app.models.refresh_token import RefreshToken
from app.models.session import Session as SessionModel
from app.models.user import User
from app.services.auth_service import issue_token_pair


TENANT_A = uuid.UUID(
    "11111111-1111-1111-1111-111111111111"
)

TENANT_B = uuid.UUID(
    "22222222-2222-2222-2222-222222222222"
)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


def create_test_user(db, prefix="api", tenant_id=TENANT_A):
    user = User(
        tenant_id=tenant_id,
        username=f"{prefix}_{uuid.uuid4().hex[:8]}",
        email=f"{prefix}_{uuid.uuid4().hex[:8]}@example.com",
        password_hash="test-hash",
        status="ACTIVE",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def cleanup_db(db):
    db.rollback()
    db.query(RefreshToken).delete()
    db.query(SessionModel).delete()
    db.query(User).delete()
    db.commit()


def auth_headers(access_token):
    return {
        "Authorization": f"Bearer {access_token}",
    }


def test_list_sessions_returns_authenticated_users_sessions():
    db = SessionLocal()

    try:
        user = create_test_user(db, "list")

        access_token_1, _ = issue_token_pair(db, user)
        access_token_2, _ = issue_token_pair(db, user)

        response = client.get(
            "/api/v1/auth/sessions",
            headers=auth_headers(access_token_2),
        )

        assert response.status_code == 200

        body = response.json()

        assert "sessions" in body
        assert len(body["sessions"]) == 2

        returned_user_ids = {
            session["user_id"]
            for session in body["sessions"]
        }

        assert returned_user_ids == {str(user.id)}

    finally:
        cleanup_db(db)
        db.close()


def test_get_session_returns_owned_session():
    db = SessionLocal()

    try:
        user = create_test_user(db, "detail")

        access_token, _ = issue_token_pair(db, user)

        session = (
            db.query(SessionModel)
            .filter(SessionModel.user_id == user.id)
            .first()
        )

        assert session is not None

        response = client.get(
            f"/api/v1/auth/sessions/{session.id}",
            headers=auth_headers(access_token),
        )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == str(session.id)
        assert body["user_id"] == str(user.id)
        assert body["tenant_id"] == str(user.tenant_id)

    finally:
        cleanup_db(db)
        db.close()


def test_get_session_rejects_other_users_session():
    db = SessionLocal()

    try:
        owner = create_test_user(db, "owner")
        other_user = create_test_user(db, "other")

        owner_access_token, _ = issue_token_pair(db, owner)
        issue_token_pair(db, other_user)

        other_session = (
            db.query(SessionModel)
            .filter(SessionModel.user_id == other_user.id)
            .first()
        )

        assert other_session is not None

        response = client.get(
            f"/api/v1/auth/sessions/{other_session.id}",
            headers=auth_headers(owner_access_token),
        )

        assert response.status_code == 404

    finally:
        cleanup_db(db)
        db.close()


def test_revoke_session_revokes_session_and_refresh_tokens():
    db = SessionLocal()

    try:
        user = create_test_user(db, "revoke")

        access_token, refresh_token = issue_token_pair(db, user)

        session = (
            db.query(SessionModel)
            .filter(SessionModel.user_id == user.id)
            .first()
        )

        stored_token = (
            db.query(RefreshToken)
            .filter(RefreshToken.session_id == session.id)
            .first()
        )

        assert session is not None
        assert stored_token is not None

        response = client.post(
            f"/api/v1/auth/sessions/{session.id}/revoke",
            headers=auth_headers(access_token),
        )

        assert response.status_code == 200

        db.expire_all()

        revoked_session = (
            db.query(SessionModel)
            .filter(SessionModel.id == session.id)
            .first()
        )

        revoked_token = (
            db.query(RefreshToken)
            .filter(RefreshToken.id == stored_token.id)
            .first()
        )

        assert revoked_session.is_active is False
        assert revoked_token.revoked is True

    finally:
        cleanup_db(db)
        db.close()


def test_revoke_all_revokes_all_user_sessions():
    db = SessionLocal()

    try:
        user = create_test_user(db, "revoke_all")

        access_token_1, _ = issue_token_pair(db, user)
        issue_token_pair(db, user)
        issue_token_pair(db, user)

        assert (
            db.query(SessionModel)
            .filter(SessionModel.user_id == user.id)
            .count()
            == 3
        )

        response = client.post(
            "/api/v1/auth/sessions/revoke-all",
            headers=auth_headers(access_token_1),
        )

        assert response.status_code == 200

        db.expire_all()

        active_sessions = (
            db.query(SessionModel)
            .filter(
                SessionModel.user_id == user.id,
                SessionModel.is_active.is_(True),
            )
            .count()
        )

        active_tokens = (
            db.query(RefreshToken)
            .join(
                SessionModel,
                RefreshToken.session_id == SessionModel.id,
            )
            .filter(
                RefreshToken.user_id == user.id,
                RefreshToken.revoked.is_(False),
            )
            .count()
        )

        assert active_sessions == 0
        assert active_tokens == 0

    finally:
        cleanup_db(db)
        db.close()


def test_revoked_access_token_returns_401_from_api():
    db = SessionLocal()

    try:
        user = create_test_user(db, "access_revoked")

        access_token, _ = issue_token_pair(db, user)

        session = (
            db.query(SessionModel)
            .filter(SessionModel.user_id == user.id)
            .first()
        )

        assert session is not None

        session.is_active = False
        db.commit()

        response = client.get(
            "/api/v1/auth/profile",
            headers=auth_headers(access_token),
        )

        assert response.status_code == 401

        body = response.json()

        assert body["error_code"] == "INVALID_SESSION"

    finally:
        cleanup_db(db)
        db.close()


def test_expired_access_token_session_returns_401_from_api():
    db = SessionLocal()

    try:
        user = create_test_user(db, "access_expired")

        access_token, _ = issue_token_pair(db, user)

        session = (
            db.query(SessionModel)
            .filter(SessionModel.user_id == user.id)
            .first()
        )

        assert session is not None

        session.expires_at = (
            datetime.now(timezone.utc)
            - timedelta(minutes=1)
        )
        db.commit()

        response = client.get(
            "/api/v1/auth/profile",
            headers=auth_headers(access_token),
        )

        assert response.status_code == 401

        body = response.json()

        assert body["error_code"] == "INVALID_SESSION"

    finally:
        cleanup_db(db)
        db.close()


def test_logout_revokes_current_session_and_refresh_token():
    db = SessionLocal()

    try:
        user = create_test_user(db, "logout")

        access_token, refresh_token = issue_token_pair(db, user)

        session = (
            db.query(SessionModel)
            .filter(SessionModel.user_id == user.id)
            .first()
        )

        assert session is not None

        response = client.post(
            "/api/v1/auth/logout",
            headers=auth_headers(access_token),
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200

        db.expire_all()

        revoked_session = (
            db.query(SessionModel)
            .filter(SessionModel.id == session.id)
            .first()
        )

        stored_token = (
            db.query(RefreshToken)
            .filter(RefreshToken.session_id == session.id)
            .first()
        )

        assert revoked_session is not None
        assert revoked_session.is_active is False

        assert stored_token is not None
        assert stored_token.revoked is True

        profile_response = client.get(
            "/api/v1/auth/profile",
            headers=auth_headers(access_token),
        )

        assert profile_response.status_code == 401

        body = profile_response.json()
        assert body["error_code"] == "INVALID_SESSION"

    finally:
        cleanup_db(db)
        db.close()


def test_get_session_rejects_cross_tenant_session():
    db = SessionLocal()

    try:
        user = create_test_user(db, "tenant", tenant_id=TENANT_A)

        access_token, _ = issue_token_pair(db, user)

        cross_tenant_session = SessionModel(
            id=uuid.uuid4(),
            user_id=user.id,
            tenant_id=TENANT_B,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            is_active=True,
        )

        db.add(cross_tenant_session)
        db.commit()
        db.refresh(cross_tenant_session)

        response = client.get(
            f"/api/v1/auth/sessions/{cross_tenant_session.id}",
            headers=auth_headers(access_token),
        )

        assert response.status_code == 404

    finally:
        cleanup_db(db)
        db.close()


def test_login_creates_session_and_hashed_refresh_token():
    db = SessionLocal()

    try:
        from app.services.auth_service import hash_password
        from app.repositories.refresh_token_repository import hash_refresh_token

        password = "TestPassword123!"

        user = User(
            tenant_id=TENANT_A,
            username=f"login_{uuid.uuid4().hex[:8]}",
            email=f"login_{uuid.uuid4().hex[:8]}@example.com",
            password_hash=hash_password(password),
            status="ACTIVE",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": user.email,
                "password": password,
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"].lower() == "bearer"

        session = (
            db.query(SessionModel)
            .filter(SessionModel.user_id == user.id)
            .first()
        )

        assert session is not None
        assert session.is_active is True
        assert session.expires_at is not None
        assert not hasattr(session, "session_token")

        stored_token = (
            db.query(RefreshToken)
            .filter(RefreshToken.session_id == session.id)
            .first()
        )

        assert stored_token is not None
        assert stored_token.token_hash == hash_refresh_token(
            body["refresh_token"]
        )
        assert stored_token.token_hash != body["refresh_token"]

    finally:
        cleanup_db(db)
        db.close()


def test_list_sessions_cleans_up_expired_sessions():
    db = SessionLocal()

    try:
        user = create_test_user(db, "cleanup")

        access_token, _ = issue_token_pair(db, user)

        expired_session = SessionModel(
            id=uuid.uuid4(),
            user_id=user.id,
            tenant_id=user.tenant_id,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            is_active=True,
        )

        db.add(expired_session)
        db.commit()
        db.refresh(expired_session)

        response = client.get(
            "/api/v1/auth/sessions",
            headers=auth_headers(access_token),
        )

        assert response.status_code == 200

        db.expire_all()

        cleaned_session = (
            db.query(SessionModel)
            .filter(SessionModel.id == expired_session.id)
            .first()
        )

        assert cleaned_session is not None
        assert cleaned_session.is_active is False

    finally:
        cleanup_db(db)
        db.close()
