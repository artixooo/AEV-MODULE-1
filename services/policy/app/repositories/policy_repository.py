"""
Policy Repository — pure data-access layer for RBAC.

No business logic lives here. Every function takes a SQLAlchemy Session
and returns ORM objects (or None), or performs a direct existence check.
This keeps the evaluation logic in policy_service.py testable in isolation
from the database, and keeps the database queries reusable across
future service-layer functions without duplicating query logic.

Week 4 (#93) addition: get_role_by_code and list_roles now optionally
accept an organization_id scope. When provided, only a role that
either belongs to that exact organization, or is a global/system role
(organization_id IS NULL), will be matched — a role belonging to a
*different* organization is treated identically to a role that
doesn't exist at all, so callers can't distinguish "wrong org" from
"no such role".

Author: Utkarsh Pratham (Squad Lead), Narayanan Varadarajan & Pratik
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.policy_models import Role, Permission, RolePermission


def get_role_by_code(db: Session, role_code: str, organization_id: Optional[str] = None) -> Optional[Role]:
    """
    Fetch a single active role by its unique role_code.

    If organization_id is given, only matches a role scoped to that
    organization or a global role (organization_id IS NULL). A role
    that belongs to a *different* organization is not matched.
    """
    query = db.query(Role).filter(Role.role_code == role_code, Role.status == "ACTIVE")
    if organization_id is not None:
        query = query.filter(or_(Role.organization_id == organization_id, Role.organization_id.is_(None)))
    return query.first()


def get_permission_by_code(db: Session, permission_code: str) -> Optional[Permission]:
    """Fetch a single permission by its unique permission_code."""
    return (
        db.query(Permission)
        .filter(Permission.permission_code == permission_code)
        .first()
    )


def list_roles(db: Session, organization_id: Optional[str] = None) -> list[Role]:
    """List all active roles, optionally scoped to an organization (plus global roles)."""
    query = db.query(Role).filter(Role.status == "ACTIVE")
    if organization_id is not None:
        query = query.filter(or_(Role.organization_id == organization_id, Role.organization_id.is_(None)))
    return query.order_by(Role.role_name).all()


def list_permissions(db: Session) -> list[Permission]:
    """List all permissions."""
    return db.query(Permission).order_by(Permission.permission_code).all()


def get_permissions_for_role(db: Session, role_id) -> list[Permission]:
    """List every permission granted to a given role."""
    role = (
        db.query(Role)
        .options(joinedload(Role.permissions))
        .filter(Role.id == role_id)
        .first()
    )
    return role.permissions if role else []


def role_has_permission(db: Session, role_id, permission_id) -> bool:
    """
    Direct existence check on the role_permissions join table.

    Deliberately a plain EXISTS-style query rather than loading full
    Permission objects — this is the hot path for /evaluate and should
    stay as cheap as possible.
    """
    return (
        db.query(RolePermission)
        .filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        .first()
        is not None
    )