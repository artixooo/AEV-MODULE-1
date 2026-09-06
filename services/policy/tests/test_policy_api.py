"""
Policy API Tests — Issue #61.

End-to-end tests: real HTTP requests through TestClient, real JWT auth
(tokens created exactly like Identity Service creates them), and a real
database. Covers authentication enforcement, service-credential
enforcement on /evaluate, and the actual RBAC evaluation decision
through the full stack.

Uses a temporary SQLite *file* (not :memory:) via TEST_DATABASE_URL,
set before the app is imported, since an in-memory SQLite database can
behave inconsistently when accessed from the background thread
FastAPI's TestClient uses to run request handlers. A real file has no
such ambiguity.

Two defensive measures for cross-test-file isolation, both needed
together in this codebase:

1. The file-based test DB above.
2. Explicitly sets app.dependency_overrides[get_db] to our own,
   properly-seeded session — rather than relying on the app's default
   get_db(). This is necessary because another test module in this
   suite (test_policy_service.py) also sets app.dependency_overrides
   at import time, pointing at its own separate, empty database; since
   `app` is a shared singleton across every test file in the same
   pytest run, that override would otherwise silently redirect our
   requests to an empty database too. We re-assert our own override
   inside this fixture (which runs at test-execution time, after all
   files have finished importing) and restore whatever was there
   before on teardown, so we don't interfere with that other file's
   own tests.

Author: Utkarsh Pratham (Squad Lead) & Narayanan Varadarajan
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

import os
import pathlib

_TEST_DB_PATH = pathlib.Path(__file__).parent / "_test_policy_api.db"
os.environ["TEST_DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH.as_posix()}"

import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi.testclient import TestClient

import app.models.policy_models as m
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal, get_db
from app.main import app


def _override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    editor_role = m.Role(role_name="Editor", role_code="editor")
    viewer_role = m.Role(role_name="Viewer", role_code="viewer")
    edit_permission = m.Permission(
        permission_name="Edit Articles",
        permission_code="articles:edit",
        resource="articles",
        action="edit",
    )
    session.add_all([editor_role, viewer_role, edit_permission])
    session.commit()

    session.add(m.RolePermission(role_id=editor_role.id, permission_id=edit_permission.id))
    session.commit()
    session.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = _override_get_db

    yield

    if previous_override is not None:
        app.dependency_overrides[get_db] = previous_override
    else:
        app.dependency_overrides.pop(get_db, None)

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if _TEST_DB_PATH.exists():
        _TEST_DB_PATH.unlink()


client = TestClient(app)


def make_token(email: str = "alice@example.com") -> str:
    """Create a token exactly the way Identity Service does."""
    payload = {"sub": email, "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


AUTH_HEADERS = {"Authorization": f"Bearer {make_token()}"}
SERVICE_HEADERS = {**AUTH_HEADERS, "X-Service-API-Key": settings.SERVICE_API_KEY}


def test_roles_endpoint_requires_auth():
    response = client.get("/api/v1/policy/roles")
    assert response.status_code == 401


def test_list_roles():
    response = client.get("/api/v1/policy/roles", headers=AUTH_HEADERS)
    assert response.status_code == 200
    codes = {r["role_code"] for r in response.json()}
    assert codes == {"editor", "viewer"}


def test_list_permissions():
    response = client.get("/api/v1/policy/permissions", headers=AUTH_HEADERS)
    assert response.status_code == 200
    codes = {p["permission_code"] for p in response.json()}
    assert "articles:edit" in codes


def test_evaluate_allow():
    response = client.post(
        "/api/v1/policy/evaluate",
        json={"role_code": "editor", "permission_code": "articles:edit"},
        headers=SERVICE_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["effect"] == "ALLOW"
    assert body["allowed"] is True


def test_evaluate_deny_missing_mapping():
    response = client.post(
        "/api/v1/policy/evaluate",
        json={"role_code": "viewer", "permission_code": "articles:edit"},
        headers=SERVICE_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["effect"] == "DENY"
    assert body["reason"] == "role_missing_permission"


def test_evaluate_requires_auth():
    # Service key present, but no JWT — should still be rejected.
    response = client.post(
        "/api/v1/policy/evaluate",
        json={"role_code": "editor", "permission_code": "articles:edit"},
        headers={"X-Service-API-Key": settings.SERVICE_API_KEY},
    )
    assert response.status_code == 401


def test_evaluate_rejects_expired_token():
    expired_payload = {
        "sub": "alice@example.com",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    expired_token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    response = client.post(
        "/api/v1/policy/evaluate",
        json={"role_code": "editor", "permission_code": "articles:edit"},
        headers={"Authorization": f"Bearer {expired_token}", "X-Service-API-Key": settings.SERVICE_API_KEY},
    )
    assert response.status_code == 401


def test_evaluate_requires_service_credential():
    """A valid, authenticated end-user JWT alone is not enough for /evaluate."""
    response = client.post(
        "/api/v1/policy/evaluate",
        json={"role_code": "editor", "permission_code": "articles:edit"},
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 422


def test_evaluate_rejects_wrong_service_credential():
    response = client.post(
        "/api/v1/policy/evaluate",
        json={"role_code": "editor", "permission_code": "articles:edit"},
        headers={**AUTH_HEADERS, "X-Service-API-Key": "definitely-wrong-key"},
    )
    assert response.status_code == 403