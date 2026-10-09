"""
RBAC Evaluation Tests — Issue #61.

Covers the repository + service layer together: given seeded roles,
permissions, and role-permission mappings, confirm evaluate_permission()
returns the correct ALLOW/DENY decision for every case, including both
"not found" edge cases. Runs entirely against in-memory SQLite.

Author: Pod Alpha Security Engineering
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models.policy_models as m
from app.core.database import Base
from app.services.policy_service import evaluate_permission

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    """Fresh in-memory schema + seed data for every test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

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

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


def test_role_with_permission_is_allowed(db):
    """A role that has been granted a permission -> ALLOW."""
    result = evaluate_permission(db, "editor", "articles:edit")
    assert result.effect == "ALLOW"
    assert result.reason == "role_has_permission"
    assert result.allowed is True


def test_role_without_permission_is_denied(db):
    """A real role, a real permission, but no mapping between them -> DENY."""
    result = evaluate_permission(db, "viewer", "articles:edit")
    assert result.effect == "DENY"
    assert result.reason == "role_missing_permission"
    assert result.allowed is False


def test_unknown_role_is_denied(db):
    """A role code that doesn't exist -> DENY, not an error."""
    result = evaluate_permission(db, "ghost", "articles:edit")
    assert result.effect == "DENY"
    assert result.reason == "role_not_found"


def test_unknown_permission_is_denied(db):
    """A permission code that doesn't exist -> DENY, not an error."""
    result = evaluate_permission(db, "editor", "nukes:launch")
    assert result.effect == "DENY"
    assert result.reason == "permission_not_found"