"""
Policy Evaluation Service — RBAC-only decision logic.

Scope (Issue #61): pure Role-Based Access Control. Given a role and a
requested permission, decide ALLOW or DENY. This deliberately does NOT
evaluate ABAC conditions (Policy.conditions), Segregation of Duties
rules, or apply caching — those are out of scope for this issue and
will be addressed in a future issue if/when it's picked up.

Author: Utkarsh Pratham (Squad Lead) & Narayanan Varadarajan
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.repositories import policy_repository


@dataclass
class EvaluationResult:
    """
    Standardized authorization decision.

    effect: "ALLOW" or "DENY"
    reason: short machine-readable code explaining the decision —
            useful for logging/debugging without leaking internals
            in the HTTP response if the caller doesn't need detail.
    """
    effect: str
    reason: str

    @property
    def allowed(self) -> bool:
        return self.effect == "ALLOW"


def evaluate_permission(db: Session, role_code: str, permission_code: str) -> EvaluationResult:
    """
    Decide whether a given role has a given permission.

    This is a pure RBAC check: role -> role_permissions -> permission.
    No attribute/condition evaluation (ABAC) is performed here.
    """
    role = policy_repository.get_role_by_code(db, role_code)
    if role is None:
        return EvaluationResult(effect="DENY", reason="role_not_found")

    permission = policy_repository.get_permission_by_code(db, permission_code)
    if permission is None:
        return EvaluationResult(effect="DENY", reason="permission_not_found")

    has_permission = policy_repository.role_has_permission(db, role.id, permission.id)
    if has_permission:
        return EvaluationResult(effect="ALLOW", reason="role_has_permission")

    return EvaluationResult(effect="DENY", reason="role_missing_permission")