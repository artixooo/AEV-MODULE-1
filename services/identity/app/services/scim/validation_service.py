from __future__ import annotations

from typing import Any

from app.schemas.scim.common import (
    SCIM_GROUP_SCHEMA,
    SCIM_USER_SCHEMA,
)


class SCIMValidationError(ValueError):
    """
    Raised when a SCIM request violates the SCIM contract.
    """

    pass


def validate_schema(
    schemas: list[str],
    expected_schema: str,
) -> None:
    """
    Verify that the required SCIM schema is present.
    """

    if expected_schema not in schemas:
        raise SCIMValidationError(
            f"Required SCIM schema '{expected_schema}' is missing."
        )


def validate_user_payload(
    payload: dict[str, Any],
) -> None:
    """
    Validate the minimum SCIM User contract.
    """

    schemas = payload.get("schemas", [])

    validate_schema(
        schemas,
        SCIM_USER_SCHEMA,
    )

    if not payload.get("userName"):
        raise SCIMValidationError(
            "SCIM User requires userName."
        )


def validate_group_payload(
    payload: dict[str, Any],
) -> None:
    """
    Validate the minimum SCIM Group contract.
    """

    schemas = payload.get("schemas", [])

    validate_schema(
        schemas,
        SCIM_GROUP_SCHEMA,
    )

    if not payload.get("displayName"):
        raise SCIMValidationError(
            "SCIM Group requires displayName."
        )


USER_PATCH_PATHS = {
    "userName",
    "active",
    "displayName",
    "name",
    "emails",
    "phoneNumbers",
}

GROUP_PATCH_PATHS = {
    "displayName",
    "members",
}


def validate_patch_operations(
    operations: list[Any],
    resource_type: str | None = None,
) -> None:
    """
    Validate SCIM PATCH operations.

    Validation covers:
    - non-empty operations
    - supported operation names
    - supported attribute paths
    - required path/value combinations
    - remove operation semantics
    - resource-specific paths
    """

    if not operations:
        raise SCIMValidationError(
            "At least one PATCH operation is required."
        )

    allowed_operations = {
        "add",
        "replace",
        "remove",
    }

    normalized_resource_type = (
        resource_type.lower()
        if resource_type
        else None
    )

    if normalized_resource_type == "user":
        allowed_paths = USER_PATCH_PATHS
    elif normalized_resource_type == "group":
        allowed_paths = GROUP_PATCH_PATHS
    else:
        allowed_paths = USER_PATCH_PATHS | GROUP_PATCH_PATHS

    for operation in operations:
        operation_name = str(operation.op).strip().lower()

        if operation_name not in allowed_operations:
            raise SCIMValidationError(
                f"Unsupported PATCH operation: {operation.op}"
            )

        path = operation.path

        if path is None or not str(path).strip():
            raise SCIMValidationError(
                f"PATCH operation '{operation_name}' requires a path."
            )

        path = str(path).strip()

        if path not in allowed_paths:
            raise SCIMValidationError(
                f"Unsupported PATCH path: {path}"
            )

        if operation_name in {"add", "replace"}:
            if operation.value is None:
                raise SCIMValidationError(
                    f"PATCH operation '{operation_name}' requires a value."
                )

        if operation_name == "remove" and operation.value is not None:
            raise SCIMValidationError(
                "PATCH remove operation must not include a value."
            )

        if path == "active":
            if operation_name in {"add", "replace"}:
                if not isinstance(operation.value, bool):
                    raise SCIMValidationError(
                        "PATCH path 'active' requires a boolean value."
                    )

        if path in {"userName", "displayName"}:
            if operation_name in {"add", "replace"}:
                if not isinstance(operation.value, str):
                    raise SCIMValidationError(
                        f"PATCH path '{path}' requires a string value."
                    )