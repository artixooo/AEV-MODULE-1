from typing import Iterable

from fastapi import HTTPException, status


def has_permission(
    permissions: Iterable[str],
    required_permission: str,
) -> bool:
    """
    Check whether an authenticated identity has a required permission.

    This is an authorization placeholder for Week 3.
    Permission ownership and business rules remain outside
    the Organization Service implementation.
    """

    return required_permission in set(permissions)


def require_permission(
    permissions: Iterable[str],
    required_permission: str,
) -> None:
    """
    Require a specific permission.

    Raises HTTP 403 when the permission is not available.
    """

    if not has_permission(permissions, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )