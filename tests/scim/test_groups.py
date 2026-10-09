from app.schemas.scim.group import (
    SCIMGroupCreate,
)

from app.services.scim.group_service import (
    SCIMGroupService,
)


def test_create_group():
    service = SCIMGroupService()

    payload = SCIMGroupCreate(
        displayName="Engineering",
    )

    group = service.create_group(
        payload,
        tenant_id="tenant-a",
    )

    assert group["displayName"] == (
        "Engineering"
    )

    assert group["tenant_id"] == "tenant-a"


def test_group_tenant_isolation():
    service = SCIMGroupService()

    group = service.create_group(
        SCIMGroupCreate(
            displayName="Engineering",
        ),
        tenant_id="tenant-a",
    )

    result = service.get_group(
        group["id"],
        tenant_id="tenant-b",
    )

    assert result is None


def test_list_groups_is_tenant_aware():
    service = SCIMGroupService()

    service.create_group(
        SCIMGroupCreate(
            displayName="Engineering",
        ),
        tenant_id="tenant-a",
    )

    service.create_group(
        SCIMGroupCreate(
            displayName="Security",
        ),
        tenant_id="tenant-b",
    )

    groups = service.list_groups(
        tenant_id="tenant-a",
    )

    assert len(groups) == 1

    assert groups[0]["displayName"] == (
        "Engineering"
    )


def test_get_group():
    service = SCIMGroupService()

    group = service.create_group(
        SCIMGroupCreate(
            displayName="Engineering",
        ),
        tenant_id="tenant-a",
    )

    result = service.get_group(
        group["id"],
        tenant_id="tenant-a",
    )

    assert result is not None

    assert result["displayName"] == (
        "Engineering"
    )


def test_replace_group():
    service = SCIMGroupService()

    group = service.create_group(
        SCIMGroupCreate(
            displayName="Engineering",
        ),
        tenant_id="tenant-a",
    )

    updated = service.replace_group(
        group["id"],
        SCIMGroupCreate(
            displayName="Security",
        ),
        tenant_id="tenant-a",
    )

    assert updated is not None

    assert updated["displayName"] == (
        "Security"
    )


def test_patch_group():
    service = SCIMGroupService()

    group = service.create_group(
        SCIMGroupCreate(
            displayName="Engineering",
        ),
        tenant_id="tenant-a",
    )

    operation = type(
        "Operation",
        (),
        {
            "op": "replace",
            "path": "displayName",
            "value": "Security",
        },
    )()

    updated = service.patch_group(
        group["id"],
        [operation],
        tenant_id="tenant-a",
    )

    assert updated is not None

    assert updated["displayName"] == (
        "Security"
    )


def test_delete_group():
    service = SCIMGroupService()

    group = service.create_group(
        SCIMGroupCreate(
            displayName="Temporary",
        ),
        tenant_id="tenant-a",
    )

    deleted = service.delete_group(
        group["id"],
        tenant_id="tenant-a",
    )

    assert deleted is True

    result = service.get_group(
        group["id"],
        tenant_id="tenant-a",
    )

    assert result is None
