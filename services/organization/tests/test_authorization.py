import pytest
from fastapi import HTTPException

from app.core.authorization import has_permission, require_permission


def test_permission_is_granted():
    permissions = [
        "organization:read",
        "organization:write",
    ]

    assert has_permission(
        permissions,
        "organization:read",
    ) is True


def test_permission_is_denied():
    permissions = [
        "organization:read",
    ]

    assert has_permission(
        permissions,
        "organization:delete",
    ) is False


def test_require_permission_allows_access():
    permissions = [
        "organization:read",
    ]

    require_permission(
        permissions,
        "organization:read",
    )


def test_require_permission_denies_access():
    permissions = [
        "organization:read",
    ]

    with pytest.raises(HTTPException) as exc:
        require_permission(
            permissions,
            "organization:delete",
        )

    assert exc.value.status_code == 403