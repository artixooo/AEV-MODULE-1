"""
Policy APIs (v1) — Tenant-Aware RBAC scope.

All endpoints require a valid Bearer token (see app/middleware/auth_middleware.py).
POST /evaluate is an internal service-to-service endpoint requiring both an
authenticated user JWT and the shared internal service credential.

Author: Utkarsh Pratham (Squad Lead), Narayanan Varadarajan & Pratik
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

from typing import Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user, AuthenticatedUser
from app.middleware.service_auth_middleware import require_service_credential
from app.repositories import policy_repository
from app.services.policy_service import evaluate_permission
from app.schemas.policy_schemas import (
    RoleResponse,
    PermissionResponse,
    EvaluateRequest,
    EvaluateResponse,
)

router = APIRouter(prefix="/api/v1/policy", tags=["Policy"])


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    summary="List all active roles",
    description="Returns every active role defined in the system (e.g. 'editor', 'viewer').",
)
def list_roles(
    db: Session = Depends(get_db),
    _user: AuthenticatedUser = Depends(get_current_user),
):
    return policy_repository.list_roles(db)


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    summary="List all permissions",
    description="Returns every permission defined in the system, regardless of which roles have been granted it.",
)
def list_permissions(
    db: Session = Depends(get_db),
    _user: AuthenticatedUser = Depends(get_current_user),
):
    return policy_repository.list_permissions(db)


@router.post(
    "/evaluate",
    response_model=EvaluateResponse,
    summary="⚠️ INTERNAL SERVICE ENDPOINT — do not expose to end-user clients",
    description=(
        "**⚠️ This is an internal service-to-service endpoint. It must not be "
        "exposed directly to end users or public-facing clients — only to "
        "trusted backend callers (e.g. the API Gateway).**\n\n"
        "Tenant-Aware Role-Based Access Control check: does the subject have "
        "permission_code within the target tenant and scope? Enforces strict cross-tenant "
        "denial. Supports both explicit role_code or membership_role mapping. "
        "Requires both a valid end-user Bearer JWT and the shared X-Service-API-Key header."
    ),
)
def evaluate(
    request: EvaluateRequest,
    db: Session = Depends(get_db),
    _user: AuthenticatedUser = Depends(get_current_user),
    _service: bool = Depends(require_service_credential),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    x_org_id: Optional[str] = Header(None, alias="X-Org-ID"),
):
    # Fallback to HTTP headers if not provided in JSON body
    caller_tenant = request.tenant_id or x_tenant_id
    caller_org = request.org_id or x_org_id

    result = evaluate_permission(
        db=db,
        role_code=request.role_code,
        permission_code=request.permission_code,
        tenant_id=caller_tenant,
        target_tenant_id=request.target_tenant_id,
        org_id=caller_org,
        workspace_id=request.workspace_id,
        project_id=request.project_id,
        scope=request.scope,
        membership_role=request.membership_role,
    )
    return EvaluateResponse(
        effect=result.effect,
        reason=result.reason,
        allowed=result.allowed,
    )