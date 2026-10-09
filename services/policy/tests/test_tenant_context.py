"""
Tenant & Scope Context Authorization Tests — Week 4.

Covers:
1. Cross-tenant denial (Tenant A cannot access Tenant B resources)
2. Same-tenant authorization (Tenant A accessing Tenant A resources -> ALLOW)
3. Organization-level authorization
4. Workspace-level authorization
5. Project-level authorization
6. Scope hierarchy enforcement (Project role cannot perform Org actions -> DENY with scope_mismatch)
7. Membership role resolution (e.g., 'org_admin' -> 'admin', 'workspace_admin' -> 'editor')
8. API endpoint integration with Tenant Headers and JSON payload
9. Backward compatibility regression tests (legacy flat RBAC calls)

Author: Pod Alpha Security Engineering
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

import uuid
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from jose import jwt

import app.models.policy_models as m
from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app
from app.services.policy_service import evaluate_permission
from app.schemas.policy_schemas import ScopeLevel

# In-memory SQLite for fully isolated, fast tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    """Seed test database with roles, permissions, and role_permissions."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed Roles
    admin_role = m.Role(role_name="Admin", role_code="admin")
    editor_role = m.Role(role_name="Editor", role_code="editor")
    viewer_role = m.Role(role_name="Viewer", role_code="viewer")

    # Seed Permissions
    org_delete_perm = m.Permission(
        permission_name="Delete Organization",
        permission_code="org:delete",
        resource="organization",
        action="delete",
    )
    workspace_create_perm = m.Permission(
        permission_name="Create Workspace",
        permission_code="workspace:create",
        resource="workspace",
        action="create",
    )
    project_edit_perm = m.Permission(
        permission_name="Edit Project",
        permission_code="project:edit",
        resource="project",
        action="edit",
    )
    project_view_perm = m.Permission(
        permission_name="View Project",
        permission_code="project:view",
        resource="project",
        action="view",
    )

    session.add_all([
        admin_role, editor_role, viewer_role,
        org_delete_perm, workspace_create_perm, project_edit_perm, project_view_perm
    ])
    session.commit()

    # Admin gets all permissions
    # Editor gets project:edit and project:view
    # Viewer gets project:view
    session.add_all([
        m.RolePermission(role_id=admin_role.id, permission_id=org_delete_perm.id),
        m.RolePermission(role_id=admin_role.id, permission_id=workspace_create_perm.id),
        m.RolePermission(role_id=admin_role.id, permission_id=project_edit_perm.id),
        m.RolePermission(role_id=admin_role.id, permission_id=project_view_perm.id),
        m.RolePermission(role_id=editor_role.id, permission_id=project_edit_perm.id),
        m.RolePermission(role_id=editor_role.id, permission_id=project_view_perm.id),
        m.RolePermission(role_id=viewer_role.id, permission_id=project_view_perm.id),
    ])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    """TestClient wired with database session override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers():
    """Generate valid test JWT + internal service credential headers."""
    payload = {
        "sub": "tester@cyart.tech",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return {
        "Authorization": f"Bearer {token}",
        "X-Service-API-Key": settings.SERVICE_API_KEY,
    }


# =============================================================================
# Service Layer Unit Tests
# =============================================================================

def test_cross_tenant_access_denied(db):
    """Tenant A user trying to access Tenant B resource is strictly DENIED."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    result = evaluate_permission(
        db=db,
        role_code="admin",
        permission_code="org:delete",
        tenant_id=tenant_a,
        target_tenant_id=tenant_b,
    )

    assert result.effect == "DENY"
    assert result.reason == "cross_tenant_access_denied"
    assert not result.allowed


def test_same_tenant_access_allowed(db):
    """Same tenant caller accessing their own resource is evaluated and ALLOWED."""
    tenant_a = uuid.uuid4()

    result = evaluate_permission(
        db=db,
        role_code="admin",
        permission_code="org:delete",
        tenant_id=tenant_a,
        target_tenant_id=tenant_a,
    )

    assert result.effect == "ALLOW"
    assert result.reason == "role_has_permission"
    assert result.allowed


def test_membership_role_resolution(db):
    """Organization membership roles correctly map to RBAC roles."""
    tenant_id = uuid.uuid4()

    # org_admin maps to 'admin' role -> has org:delete
    result = evaluate_permission(
        db=db,
        role_code=None,
        membership_role="org_admin",
        permission_code="org:delete",
        tenant_id=tenant_id,
        target_tenant_id=tenant_id,
        scope=ScopeLevel.ORGANIZATION,
    )
    assert result.effect == "ALLOW"
    assert result.allowed

    # workspace_admin maps to 'editor' role -> has project:edit
    result_ws = evaluate_permission(
        db=db,
        role_code=None,
        membership_role="workspace_admin",
        permission_code="project:edit",
        tenant_id=tenant_id,
        target_tenant_id=tenant_id,
        scope=ScopeLevel.WORKSPACE,
    )
    assert result_ws.effect == "ALLOW"
    assert result_ws.allowed


def test_scope_mismatch_denial(db):
    """Project-level contributor attempting an Organization-level scope action is DENIED."""
    tenant_id = uuid.uuid4()

    result = evaluate_permission(
        db=db,
        role_code=None,
        membership_role="project_contributor",
        permission_code="org:delete",
        tenant_id=tenant_id,
        target_tenant_id=tenant_id,
        scope=ScopeLevel.ORGANIZATION,
    )
    assert result.effect == "DENY"
    assert result.reason == "scope_mismatch"
    assert not result.allowed


def test_legacy_flat_rbac_backward_compatibility(db):
    """Evaluating without tenant context executes legacy Week 3 flat RBAC."""
    result = evaluate_permission(db=db, role_code="editor", permission_code="project:edit")
    assert result.effect == "ALLOW"
    assert result.reason == "role_has_permission"

    result_denied = evaluate_permission(db=db, role_code="viewer", permission_code="project:edit")
    assert result_denied.effect == "DENY"
    assert result_denied.reason == "role_missing_permission"


# =============================================================================
# API Endpoint Integration Tests
# =============================================================================

def test_api_evaluate_cross_tenant_denial(client, auth_headers):
    """POST /evaluate returns DENY when request contains mismatched tenant IDs."""
    tenant_a = str(uuid.uuid4())
    tenant_b = str(uuid.uuid4())

    payload = {
        "role_code": "admin",
        "permission_code": "org:delete",
        "tenant_id": tenant_a,
        "target_tenant_id": tenant_b,
    }
    response = client.post("/api/v1/policy/evaluate", json=payload, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["effect"] == "DENY"
    assert data["reason"] == "cross_tenant_access_denied"
    assert data["allowed"] is False


def test_api_evaluate_tenant_header_support(client, auth_headers):
    """POST /evaluate supports X-Tenant-ID header when not in payload body."""
    tenant_id = str(uuid.uuid4())
    headers = {**auth_headers, "X-Tenant-ID": tenant_id}

    payload = {
        "role_code": "admin",
        "permission_code": "org:delete",
        "target_tenant_id": tenant_id,
    }
    response = client.post("/api/v1/policy/evaluate", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["effect"] == "ALLOW"
    assert data["reason"] == "role_has_permission"
    assert data["allowed"] is True



def test_org_scoped_role_not_reachable_from_a_different_organization(db):
    """
    Proves the Week 4 DB-backed fix: a role that genuinely belongs to one
    organization is NOT reachable when evaluated against a matching-but-
    unrelated tenant_id/target_tenant_id pair for a different organization.

    Before this fix, get_role_by_code had no organization filter at all,
    so a caller sending internally-consistent (but fabricated) tenant_id
    == target_tenant_id for org_y could still resolve a role that only
    actually exists in org_x, and get an ALLOW decision for it.
    """
    org_x = uuid.uuid4()
    org_y = uuid.uuid4()

    org_scoped_role = m.Role(role_name="Org X Admin", role_code="org-scoped-admin", organization_id=org_x)
    sensitive_perm = m.Permission(
        permission_name="Delete Everything",
        permission_code="danger:delete",
        resource="danger",
        action="delete",
    )
    db.add_all([org_scoped_role, sensitive_perm])
    db.commit()
    db.add(m.RolePermission(role_id=org_scoped_role.id, permission_id=sensitive_perm.id))
    db.commit()

    # Legitimate: caller genuinely in org_x, evaluating an org_x-scoped role
    result_legit = evaluate_permission(
        db=db,
        role_code="org-scoped-admin",
        permission_code="danger:delete",
        tenant_id=org_x,
        target_tenant_id=org_x,
    )
    assert result_legit.effect == "ALLOW"

    # The attack this closes: caller claims org_y for BOTH tenant_id and
    # target_tenant_id (internally consistent — passes the tenant_id ==
    # target_tenant_id check on its own) but the role they're naming only
    # exists in org_x, not org_y.
    result_cross_org = evaluate_permission(
        db=db,
        role_code="org-scoped-admin",
        permission_code="danger:delete",
        tenant_id=org_y,
        target_tenant_id=org_y,
    )
    assert result_cross_org.effect == "DENY"
    assert result_cross_org.reason == "role_not_found"


    
def test_project_scope_authorization(db):
    """
    Proves the previously-untested PROJECT scope level of the hierarchy:
    a project_admin membership role (max_scope=PROJECT) requesting a
    PROJECT-scoped action they genuinely have permission for is ALLOWED.
    """
    tenant_id = uuid.uuid4()

    result = evaluate_permission(
        db=db,
        role_code=None,
        membership_role="project_admin",
        permission_code="project:edit",
        tenant_id=tenant_id,
        target_tenant_id=tenant_id,
        scope=ScopeLevel.PROJECT,
    )
    assert result.effect == "ALLOW"
    assert result.reason == "role_has_permission"