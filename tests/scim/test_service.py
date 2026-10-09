from app.schemas.scim.group import SCIMGroupCreate
from app.schemas.scim.user import SCIMUserCreate
from app.services.scim.group_service import SCIMGroupService
from app.services.scim.user_service import SCIMUserService


TENANT_A = "tenant-a"
TENANT_B = "tenant-b"


def test_user_service_enforces_tenant_isolation():
    service = SCIMUserService()

    payload = SCIMUserCreate(
        userName="alice",
        active=True,
    )

    user = service.create_user(payload, TENANT_A)
    user_id = user["id"]

    assert service.get_user(user_id, TENANT_A) is not None
    assert service.get_user(user_id, TENANT_B) is None

    replacement = SCIMUserCreate(
        userName="alice-updated",
        active=True,
    )

    assert service.replace_user(user_id, replacement, TENANT_B) is None
    assert service.get_user(user_id, TENANT_A)["userName"] == "alice"

    patch_operation = type(
        "PatchOperation",
        (),
        {
            "op": "replace",
            "path": "active",
            "value": False,
        },
    )()

    assert service.patch_user(user_id, [patch_operation], TENANT_B) is None
    assert service.get_user(user_id, TENANT_A)["active"] is True

    assert service.delete_user(user_id, TENANT_B) is False
    assert service.get_user(user_id, TENANT_A) is not None


def test_user_service_list_is_tenant_scoped():
    service = SCIMUserService()

    service.create_user(
        SCIMUserCreate(userName="alice"),
        TENANT_A,
    )
    service.create_user(
        SCIMUserCreate(userName="bob"),
        TENANT_B,
    )

    tenant_a_users = service.list_users(TENANT_A)
    tenant_b_users = service.list_users(TENANT_B)

    assert len(tenant_a_users) == 1
    assert tenant_a_users[0]["userName"] == "alice"

    assert len(tenant_b_users) == 1
    assert tenant_b_users[0]["userName"] == "bob"


def test_group_service_enforces_tenant_isolation():
    service = SCIMGroupService()

    payload = SCIMGroupCreate(
        displayName="Engineering",
    )

    group = service.create_group(payload, TENANT_A)
    group_id = group["id"]

    assert service.get_group(group_id, TENANT_A) is not None
    assert service.get_group(group_id, TENANT_B) is None

    replacement = SCIMGroupCreate(
        displayName="Engineering Updated",
    )

    assert service.replace_group(group_id, replacement, TENANT_B) is None
    assert service.get_group(group_id, TENANT_A)["displayName"] == "Engineering"

    patch_operation = type(
        "PatchOperation",
        (),
        {
            "op": "replace",
            "path": "displayName",
            "value": "Unauthorized Update",
        },
    )()

    assert service.patch_group(group_id, [patch_operation], TENANT_B) is None
    assert (
        service.get_group(group_id, TENANT_A)["displayName"]
        == "Engineering"
    )

    assert service.delete_group(group_id, TENANT_B) is False
    assert service.get_group(group_id, TENANT_A) is not None


def test_group_service_list_is_tenant_scoped():
    service = SCIMGroupService()

    service.create_group(
        SCIMGroupCreate(displayName="Engineering"),
        TENANT_A,
    )
    service.create_group(
        SCIMGroupCreate(displayName="Security"),
        TENANT_B,
    )

    tenant_a_groups = service.list_groups(TENANT_A)
    tenant_b_groups = service.list_groups(TENANT_B)

    assert len(tenant_a_groups) == 1
    assert tenant_a_groups[0]["displayName"] == "Engineering"

    assert len(tenant_b_groups) == 1
    assert tenant_b_groups[0]["displayName"] == "Security"