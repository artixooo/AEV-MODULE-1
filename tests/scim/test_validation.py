import pytest

from app.schemas.scim.common import (
    SCIM_GROUP_SCHEMA,
    SCIM_USER_SCHEMA,
)

from app.services.scim.validation_service import (
    SCIMValidationError,
    validate_group_payload,
    validate_patch_operations,
    validate_user_payload,
)


def test_valid_user_payload():
    payload = {
        "schemas": [
            SCIM_USER_SCHEMA,
        ],
        "userName": "gunavardhan@example.com",
    }

    validate_user_payload(payload)


def test_user_requires_username():
    payload = {
        "schemas": [
            SCIM_USER_SCHEMA,
        ],
    }

    with pytest.raises(SCIMValidationError):
        validate_user_payload(payload)


def test_user_requires_correct_schema():
    payload = {
        "schemas": [
            SCIM_GROUP_SCHEMA,
        ],
        "userName": "user@example.com",
    }

    with pytest.raises(SCIMValidationError):
        validate_user_payload(payload)


def test_valid_group_payload():
    payload = {
        "schemas": [
            SCIM_GROUP_SCHEMA,
        ],
        "displayName": "Engineering",
    }

    validate_group_payload(payload)


def test_group_requires_display_name():
    payload = {
        "schemas": [
            SCIM_GROUP_SCHEMA,
        ],
    }

    with pytest.raises(SCIMValidationError):
        validate_group_payload(payload)


def test_group_requires_correct_schema():
    payload = {
        "schemas": [
            SCIM_USER_SCHEMA,
        ],
        "displayName": "Engineering",
    }

    with pytest.raises(SCIMValidationError):
        validate_group_payload(payload)


def test_empty_patch_operations_rejected():
    with pytest.raises(SCIMValidationError):
        validate_patch_operations([])


def test_invalid_patch_operation_rejected():
    operation = type(
        "Operation",
        (),
        {
            "op": "invalid",
        },
    )()

    with pytest.raises(SCIMValidationError):
        validate_patch_operations(
            [operation]
        )


def test_valid_patch_operations():
    operations = [
        type(
            "Operation",
            (),
            {
                "op": "replace",
                "path": "userName",
                "value": "updated-user",
            },
        )(),
        type(
            "Operation",
            (),
            {
                "op": "add",
                "path": "active",
                "value": True,
            },
        )(),
        type(
            "Operation",
            (),
            {
                "op": "remove",
                "path": "emails",
                "value": None,
            },
        )(),
    ]

    validate_patch_operations(
        operations,
        resource_type="user",
    )
