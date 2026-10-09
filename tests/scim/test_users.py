from app.schemas.scim.user import (
    SCIMUserCreate,
)

from app.services.scim.user_service import (
    SCIMUserService,
)


def test_create_user():
    service = SCIMUserService()

    payload = SCIMUserCreate(
        userName="gunavardhan@example.com",
        active=True,
    )

    user = service.create_user(
        payload,
        tenant_id="tenant-a",
    )

    assert user["userName"] == (
        "gunavardhan@example.com"
    )

    assert user["tenant_id"] == "tenant-a"

    assert user["active"] is True


def test_tenant_isolation():
    service = SCIMUserService()

    payload = SCIMUserCreate(
        userName="user@example.com",
    )

    user = service.create_user(
        payload,
        tenant_id="tenant-a",
    )

    result = service.get_user(
        user["id"],
        tenant_id="tenant-b",
    )

    assert result is None


def test_user_list_is_tenant_aware():
    service = SCIMUserService()

    service.create_user(
        SCIMUserCreate(
            userName="a@example.com",
        ),
        tenant_id="tenant-a",
    )

    service.create_user(
        SCIMUserCreate(
            userName="b@example.com",
        ),
        tenant_id="tenant-b",
    )

    users = service.list_users(
        tenant_id="tenant-a",
    )

    assert len(users) == 1

    assert users[0]["userName"] == (
        "a@example.com"
    )


def test_get_user():
    service = SCIMUserService()

    user = service.create_user(
        SCIMUserCreate(
            userName="get@example.com",
        ),
        tenant_id="tenant-a",
    )

    result = service.get_user(
        user["id"],
        tenant_id="tenant-a",
    )

    assert result is not None

    assert result["userName"] == (
        "get@example.com"
    )


def test_replace_user():
    service = SCIMUserService()

    user = service.create_user(
        SCIMUserCreate(
            userName="old@example.com",
        ),
        tenant_id="tenant-a",
    )

    updated = service.replace_user(
        user["id"],
        SCIMUserCreate(
            userName="new@example.com",
        ),
        tenant_id="tenant-a",
    )

    assert updated is not None

    assert updated["userName"] == (
        "new@example.com"
    )


def test_patch_user():
    service = SCIMUserService()

    user = service.create_user(
        SCIMUserCreate(
            userName="patch@example.com",
        ),
        tenant_id="tenant-a",
    )

    operation = type(
        "Operation",
        (),
        {
            "op": "replace",
            "path": "active",
            "value": False,
        },
    )()

    updated = service.patch_user(
        user["id"],
        [operation],
        tenant_id="tenant-a",
    )

    assert updated is not None

    assert updated["active"] is False


def test_delete_user():
    service = SCIMUserService()

    user = service.create_user(
        SCIMUserCreate(
            userName="delete@example.com",
        ),
        tenant_id="tenant-a",
    )

    deleted = service.delete_user(
        user["id"],
        tenant_id="tenant-a",
    )

    assert deleted is True

    result = service.get_user(
        user["id"],
        tenant_id="tenant-a",
    )

    assert result is None
