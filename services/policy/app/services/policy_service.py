"""
Policy Evaluation Service — Tenant-Aware RBAC Decision Logic.

Scope: Role-Based Access Control (RBAC) extended with Tenant Context
and hierarchical scopes (Organization, Workspace, Project).

Evaluates:
1. Tenant Isolation: Rejects cross-tenant access attempts immediately.
2. Membership-to-Role Mapping: Resolves Organization Service membership roles.
3. Scope Hierarchy: Enforces scope boundaries (org -> workspace -> project).
4. Pure RBAC: role -> role_permissions -> permission evaluation.

Author: Utkarsh Pratham (Squad Lead), Narayanan Varadarajan & Pratik
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

import uuid
from dataclasses import dataclass
from typing import Optional, Union
from sqlalchemy.orm import Session

from app.repositories import policy_repository
from app.schemas.policy_schemas import (
    ScopeLevel,
    DEFAULT_MEMBERSHIP_ROLE_MAPPINGS,
)


@dataclass
class EvaluationResult:
    """
    Standardized authorization decision.

    effect: "ALLOW" or "DENY"
    reason: short machine-readable code explaining the decision:
            - role_has_permission
            - role_missing_permission
            - role_not_found
            - permission_not_found
            - cross_tenant_access_denied
            - scope_mismatch
            - invalid_context
    """
    effect: str
    reason: str

    @property
    def allowed(self) -> bool:
        return self.effect == "ALLOW"


# Scope hierarchy weight (higher weight = broader authority)
SCOPE_HIERARCHY = {
    ScopeLevel.ORGANIZATION.value: 3,
    ScopeLevel.WORKSPACE.value: 2,
    ScopeLevel.PROJECT.value: 1,
}


def evaluate_permission(
    db: Session,
    role_code: Optional[str],
    permission_code: str,
    tenant_id: Optional[Union[uuid.UUID, str]] = None,
    target_tenant_id: Optional[Union[uuid.UUID, str]] = None,
    org_id: Optional[Union[uuid.UUID, str]] = None,
    workspace_id: Optional[Union[uuid.UUID, str]] = None,
    project_id: Optional[Union[uuid.UUID, str]] = None,
    scope: Optional[Union[ScopeLevel, str]] = None,
    membership_role: Optional[str] = None,
) -> EvaluationResult:
    """
    Decide whether a given subject has permission within the provided tenant and scope context.

    Workflow:
    1. Tenant Isolation: If caller tenant_id and target_tenant_id are both supplied,
       strictly enforce tenant_id == target_tenant_id.
    2. Membership Role Resolution: If role_code is missing but membership_role is supplied,
       map membership_role to the canonical RBAC role code.
    3. Scope Hierarchy Validation: If scope is specified, ensure membership role permissions
       satisfy the scope hierarchy.
    4. RBAC Evaluation: Query repository for role-to-permission mapping.
    """
    # -------------------------------------------------------------------------
    # 1. Tenant Isolation Check (Zero Trust)
    # -------------------------------------------------------------------------
    if tenant_id is not None and target_tenant_id is not None:
        if str(tenant_id).lower() != str(target_tenant_id).lower():
            return EvaluationResult(
                effect="DENY",
                reason="cross_tenant_access_denied",
            )

    # -------------------------------------------------------------------------
    # 2. Membership-to-Role Mapping & Scope Boundary
    # -------------------------------------------------------------------------
    effective_role_code = role_code
    membership_max_scope = None

    if membership_role:
        norm_membership = membership_role.strip().lower()
        if norm_membership in DEFAULT_MEMBERSHIP_ROLE_MAPPINGS:
            mapping = DEFAULT_MEMBERSHIP_ROLE_MAPPINGS[norm_membership]
            if not effective_role_code:
                effective_role_code = mapping["role_code"]
            membership_max_scope = mapping["max_scope"]
        elif not effective_role_code:
            # Fallback to direct name if not in standard mapping table
            effective_role_code = norm_membership

    if not effective_role_code:
        return EvaluationResult(effect="DENY", reason="role_not_found")

    # -------------------------------------------------------------------------
    # 3. Scope Hierarchy Evaluation
    # -------------------------------------------------------------------------
    if scope:
        scope_str = scope.value if isinstance(scope, ScopeLevel) else str(scope).lower()
        if membership_max_scope and scope_str in SCOPE_HIERARCHY:
            user_scope_level = SCOPE_HIERARCHY.get(membership_max_scope, 0)
            required_scope_level = SCOPE_HIERARCHY.get(scope_str, 0)

            # If user's max scope is narrower than the requested action's scope, deny access
            if user_scope_level < required_scope_level:
                return EvaluationResult(
                    effect="DENY",
                    reason="scope_mismatch",
                )

    # -------------------------------------------------------------------------
    # 4. Standard RBAC Repository Evaluation
    # -------------------------------------------------------------------------
    # Week 4 fix: scope the role lookup itself to the target organization,
    # not just compare tenant_id/target_tenant_id as caller-supplied values
    # against each other. This makes cross-tenant denial real and DB-backed:
    # even if a caller sends matching (but fabricated) tenant_id/
    # target_tenant_id, the role they're claiming must actually belong to
    # that organization in the database (or be a global role), or the
    # lookup fails and returns role_not_found.
    role = policy_repository.get_role_by_code(
        db, effective_role_code, organization_id=target_tenant_id or tenant_id
    )
    if role is None:
        return EvaluationResult(effect="DENY", reason="role_not_found")

    permission = policy_repository.get_permission_by_code(db, permission_code)
    if permission is None:
        return EvaluationResult(effect="DENY", reason="permission_not_found")

    has_permission = policy_repository.role_has_permission(db, role.id, permission.id)
    if has_permission:
        return EvaluationResult(effect="ALLOW", reason="role_has_permission")

    return EvaluationResult(effect="DENY", reason="role_missing_permission")