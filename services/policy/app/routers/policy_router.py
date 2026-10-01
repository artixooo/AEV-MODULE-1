"""
Policy APIs (v1) — RBAC scope, Issue #61.

All endpoints require a valid Bearer token (see app/middleware/auth_middleware.py).
The token proves who is calling; it does not carry role information, so
POST /evaluate takes role_code explicitly rather than deriving it from
the token.

Author: Utkarsh Pratham (Squad Lead) & Narayanan Varadarajan
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

from fastapi import APIRouter, Depends
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
        "Pure Role-Based Access Control check: does role_code have permission_code, "
        "via the role_permissions mapping? Returns DENY (not an error) if either the "
        "role or permission code does not exist. Requires both a valid end-user "
        "Bearer JWT and the shared X-Service-API-Key header — see "
        "app/middleware/service_auth_middleware.py for why the second credential "
        "is required. Does not evaluate ABAC conditions, Segregation of Duties "
        "rules, or apply caching — those are out of scope for this endpoint."
    ),
)
def evaluate(
    request: EvaluateRequest,
    db: Session = Depends(get_db),
    _user: AuthenticatedUser = Depends(get_current_user),
    _service: bool = Depends(require_service_credential),
):
    result = evaluate_permission(db, request.role_code, request.permission_code)
    return EvaluateResponse(
        effect=result.effect,
        reason=result.reason,
        allowed=result.allowed,
    )