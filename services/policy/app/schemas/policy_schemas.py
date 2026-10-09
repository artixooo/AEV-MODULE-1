"""
Pydantic Schemas — Policy Service API (v1, Tenant-Aware RBAC scope).

Author: Utkarsh Pratham (Squad Lead), Narayanan Varadarajan & Pratik
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

import uuid
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ScopeLevel(str, Enum):
    """Hierarchical authorization scope levels."""
    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    PROJECT = "project"


class TenantContext(BaseModel):
    """
    Context identifying the tenant and hierarchical container scopes.
    """
    tenant_id: uuid.UUID = Field(..., description="ID of the tenant / organization.")
    org_id: Optional[uuid.UUID] = Field(default=None, description="Specific organization ID (defaults to tenant_id).")
    workspace_id: Optional[uuid.UUID] = Field(default=None, description="Optional workspace ID within the organization.")
    project_id: Optional[uuid.UUID] = Field(default=None, description="Optional project ID within the workspace.")


class MembershipRoleMapping(BaseModel):
    """
    Defines how Organization Service membership roles map to Policy roles & scopes.
    """
    membership_role: str = Field(..., examples=["org_admin", "workspace_admin", "project_member", "viewer"])
    effective_role_code: str = Field(..., examples=["admin", "editor", "viewer"])
    allowed_scope: ScopeLevel = Field(default=ScopeLevel.ORGANIZATION)


# Predefined mapping table from Organization Service membership roles to Policy role codes and maximum scopes
DEFAULT_MEMBERSHIP_ROLE_MAPPINGS: Dict[str, Dict[str, str]] = {
    "org_owner": {"role_code": "admin", "max_scope": ScopeLevel.ORGANIZATION.value},
    "org_admin": {"role_code": "admin", "max_scope": ScopeLevel.ORGANIZATION.value},
    "workspace_admin": {"role_code": "editor", "max_scope": ScopeLevel.WORKSPACE.value},
    "workspace_member": {"role_code": "viewer", "max_scope": ScopeLevel.WORKSPACE.value},
    "project_admin": {"role_code": "editor", "max_scope": ScopeLevel.PROJECT.value},
    "project_contributor": {"role_code": "editor", "max_scope": ScopeLevel.PROJECT.value},
    "project_viewer": {"role_code": "viewer", "max_scope": ScopeLevel.PROJECT.value},
    "viewer": {"role_code": "viewer", "max_scope": ScopeLevel.PROJECT.value},
}


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role_name: str = Field(examples=["Editor"])
    role_code: str = Field(examples=["editor"])
    description: Optional[str] = None


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    permission_name: str = Field(examples=["Edit Articles"])
    permission_code: str = Field(examples=["articles:edit"])
    resource: str = Field(examples=["articles"])
    action: str = Field(examples=["edit"])


class EvaluateRequest(BaseModel):
    """
    Request body for POST /evaluate.

    Supports:
    1. Legacy flat RBAC: role_code + permission_code.
    2. Tenant-aware RBAC: tenant_id, target_tenant_id, org_id, workspace_id, project_id, scope.
    3. Membership-based RBAC: membership_role (e.g. 'org_admin') automatically mapped to role_code.
    """
    role_code: Optional[str] = Field(
        default=None,
        examples=["editor"],
        description="Explicit RBAC role code (e.g. 'editor', 'admin', 'viewer').",
    )
    permission_code: str = Field(
        ...,
        examples=["articles:edit"],
        description="Target permission code to evaluate.",
    )
    # Multi-tenant and Scope context fields (Week 4)
    tenant_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Tenant / Company ID of the calling entity.",
        examples=["a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"],
    )
    target_tenant_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Tenant ID owning the resource being accessed (must match tenant_id for multi-tenant isolation).",
        examples=["a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"],
    )
    org_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Organization ID context.",
    )
    workspace_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Workspace ID context.",
    )
    project_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Project ID context.",
    )
    scope: Optional[ScopeLevel] = Field(
        default=None,
        description="Requested scope level for authorization (organization, workspace, or project).",
    )
    membership_role: Optional[str] = Field(
        default=None,
        examples=["org_admin", "workspace_admin", "project_contributor"],
        description="Optional membership role from Organization Service to be mapped to an RBAC role.",
    )


class EvaluateResponse(BaseModel):
    """Standardized authorization decision returned to the caller."""
    effect: str = Field(examples=["ALLOW"], description="'ALLOW' or 'DENY'")
    reason: str = Field(
        examples=["role_has_permission"],
        description=(
            "Machine-readable reason code: "
            "role_has_permission, role_missing_permission, role_not_found, "
            "permission_not_found, cross_tenant_access_denied, scope_mismatch, or invalid_context."
        ),
    )
    allowed: bool = Field(examples=[True])