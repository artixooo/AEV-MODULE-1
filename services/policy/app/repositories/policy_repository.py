"""
Policy Repository — pure data-access layer for RBAC.

No business logic lives here. Every function takes a SQLAlchemy Session
and returns ORM objects (or None), or performs a direct existence check.
This keeps the evaluation logic in policy_service.py testable in isolation
from the database, and keeps the database queries reusable across
future service-layer functions without duplicating query logic.

Author: Utkarsh Pratham (Squad Lead) & Narayanan Varadarajan
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

from typing import Optional
from sqlalchemy.orm import Session, joinedload

from app.models.policy_models import Role, Permission, RolePermission


def get_role_by_code(db: Session, role_code: str) -> Optional[Role]:
    """Fetch a single active role by its unique role_code."""
    return (
        db.query(Role)
        .filter(Role.role_code == role_code, Role.status == "ACTIVE")
        .first()
    )


def get_permission_by_code(db: Session, permission_code: str) -> Optional[Permission]:
    """Fetch a single permission by its unique permission_code."""
    return (
        db.query(Permission)
        .filter(Permission.permission_code == permission_code)
        .first()
    )


def list_roles(db: Session) -> list[Role]:
    """List all active roles."""
    return db.query(Role).filter(Role.status == "ACTIVE").order_by(Role.role_name).all()


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