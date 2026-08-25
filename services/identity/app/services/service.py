import hashlib
import json
import logging
import re
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.models.policy_models import Role, Permission, RolePermission, Policy
from app.schemas.policy_schemas import EvaluationRequest, EvaluationResponse
from app.services.cache_service import cache_service
from app.services.sod_service import sod_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class EvaluationService:
    @staticmethod
    def _evaluate_single_condition(condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluates a single ABAC condition dictionary against context.
        Context has structure: {"user": ..., "resource": ..., "env": ...}
        """
        if "and" in condition:
            return all(EvaluationService._evaluate_single_condition(c, context) for c in condition["and"])
        if "or" in condition:
            return any(EvaluationService._evaluate_single_condition(c, context) for c in condition["or"])
        if "not" in condition:
            return not EvaluationService._evaluate_single_condition(condition["not"], context)

        field_path = condition.get("field", "")
        operator = condition.get("operator", "equals")
        target_val = condition.get("value")

        # Resolve field_path like "user.org_id" or "resource.classification_level"
        current = context
        field_parts = field_path.split(".")
        actual_val = None
        for part in field_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                current = None
                break
        actual_val = current

        # Resolve dynamic target_val if target_val refers to a context property (e.g., "resource.org_id")
        if isinstance(target_val, str) and "." in target_val:
            target_parts = target_val.split(".")
            if target_parts[0] in context:
                tgt_curr = context
                for part in target_parts:
                    if isinstance(tgt_curr, dict) and part in tgt_curr:
                        tgt_curr = tgt_curr[part]
                    else:
                        tgt_curr = None
                        break
                if tgt_curr is not None:
                    target_val = tgt_curr

        # Evaluate operators
        if operator == "equals":
            return actual_val == target_val
        elif operator == "not_equals":
            return actual_val != target_val
        elif operator == "in":
            return actual_val in target_val if isinstance(target_val, (list, set, tuple, str)) else False
        elif operator == "not_in":
            return actual_val not in target_val if isinstance(target_val, (list, set, tuple, str)) else True
        elif operator == "contains":
            return target_val in actual_val if isinstance(actual_val, (list, set, tuple, str)) else False
        elif operator == "greater_than":
            return actual_val > target_val if actual_val is not None and target_val is not None else False
        elif operator == "less_than":
            return actual_val < target_val if actual_val is not None and target_val is not None else False
        elif operator == "greater_than_or_equal":
            return actual_val >= target_val if actual_val is not None and target_val is not None else False
        elif operator == "less_than_or_equal":
            return actual_val <= target_val if actual_val is not None and target_val is not None else False
        elif operator == "regex_match":
            return bool(re.search(str(target_val), str(actual_val))) if actual_val is not None else False

        return False

    @staticmethod
    def _get_system_role_permissions(roles: List[str]) -> List[str]:
        """Provides default permission sets for standard system roles."""
        perms = set()
        roles_set = set(r.upper() for r in roles)

        if "SUPER_ADMIN" in roles_set:
            perms.add("*:*")
            return list(perms)

        if "PLATFORM_OPERATOR" in roles_set:
            perms.update(["organization:*", "workspace:*", "user:*", "policy:read", "audit:read"])
        if "ORG_ADMIN" in roles_set:
            perms.update(["organization:*", "workspace:*", "user:*", "policy:*", "audit:*"])
        if "WORKSPACE_ADMIN" in roles_set:
            perms.update(["workspace:*", "user:*", "policy:read", "audit:read"])
        if "EDITOR" in roles_set:
            perms.update(["*:read", "*:create", "*:update", "organization:read", "workspace:read", "user:read"])
        if "VIEWER" in roles_set:
            perms.update(["*:read", "organization:read", "workspace:read", "user:read"])
        if "AUDITOR" in roles_set:
            perms.update(["audit:read", "audit:export", "policy:read", "organization:read"])

        return list(perms)

    @staticmethod
    def get_effective_user_permissions(db: Session, user_id: str, roles: List[str]) -> Tuple[List[str], List[str]]:
        """Computes all effective permissions for a user given roles."""
        user_roles = list(roles)
        effective_perms = set(EvaluationService._get_system_role_permissions(user_roles))

        # Query database role permissions for custom roles
        db_roles = db.query(Role).filter(Role.role_code.in_(user_roles)).all()
        for role in db_roles:
            for perm in role.permissions:
                effective_perms.add(f"{perm.resource}:{perm.action}")
                effective_perms.add(perm.permission_code)

        return user_roles, sorted(list(effective_perms))

    @staticmethod
    def evaluate(db: Session, req: EvaluationRequest) -> EvaluationResponse:
        # Cache key lookup
        cache_key = hashlib.md5(json.dumps(req.model_dump(), sort_keys=True).encode()).hexdigest()
        cached_result = cache_service.get(cache_key)
        if cached_result:
            cached_result["cached"] = True
            return EvaluationResponse(**cached_result)

        # 1. Check Segregation of Duties (SoD) enforcement
        if settings.ENABLE_SOD_ENFORCEMENT and req.roles:
            sod_res = sod_service.check_conflict(db, req.roles, [])
            if sod_res.has_conflict:
                denial = EvaluationResponse(
                    allowed=False,
                    decision="DENY",
                    reason=f"Segregation of Duties Violation: {sod_res.reason}",
                    policy_code="SOD_ENFORCEMENT",
                    cached=False
                )
                logger.warning(f"PERMISSION DENIED (SoD): user={req.user_id}, resource={req.resource}, action={req.action}, reason={denial.reason}")
                cache_service.set(cache_key, denial.model_dump())
                return denial

        # 2. Check RBAC permissions
        roles, effective_permissions = EvaluationService.get_effective_user_permissions(db, req.user_id or "", req.roles)
        requested_perm = f"{req.resource}:{req.action}"
        has_rbac_permission = (
            "*:*" in effective_permissions or
            requested_perm in effective_permissions or
            f"{req.resource}:*" in effective_permissions or
            f"*:{req.action}" in effective_permissions
        )

        # 3. Check ABAC Policies
        context = {
            "user": {**req.user_attributes, "id": req.user_id, "roles": req.roles},
            "resource": {**req.resource_attributes, "type": req.resource},
            "env": req.environment
        }

        matching_policies = db.query(Policy).filter(
            Policy.status == "ACTIVE",
            Policy.resource.in_([req.resource, "*"]),
            Policy.action.in_([req.action, "*"])
        ).order_by(Policy.priority.asc()).all()

        abac_decision = None
        applied_policy_code = None

        for policy in matching_policies:
            if not policy.conditions or EvaluationService._evaluate_single_condition(policy.conditions, context):
                abac_decision = policy.effect.upper()
                applied_policy_code = policy.policy_code
                # DENY policy takes absolute precedence
                if abac_decision == "DENY":
                    break

        # Decision Synthesis
        final_allowed = False
        final_decision = "DENY"
        reason = ""

        if abac_decision == "DENY":
            final_allowed = False
            final_decision = "DENY"
            reason = f"Explicit DENY policy '{applied_policy_code}' matched"
        elif abac_decision == "ALLOW":
            final_allowed = True
            final_decision = "ALLOW"
            reason = f"ABAC Policy '{applied_policy_code}' granted access"
        elif has_rbac_permission:
            final_allowed = True
            final_decision = "ALLOW"
            reason = f"RBAC permission '{requested_perm}' granted access"
        else:
            final_allowed = False
            final_decision = "DENY"
            reason = f"No matching RBAC permission or ABAC ALLOW policy for '{requested_perm}'"

        response = EvaluationResponse(
            allowed=final_allowed,
            decision=final_decision,
            reason=reason,
            policy_code=applied_policy_code,
            cached=False
        )

        if not final_allowed:
            logger.warning(f"PERMISSION DENIED (FR-AUTHZ-008): user={req.user_id}, roles={req.roles}, resource={req.resource}, action={req.action}, reason={reason}")

        cache_service.set(cache_key, response.model_dump())
        return response


evaluation_service = EvaluationService()
