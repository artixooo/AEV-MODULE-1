from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.schemas.scim.group import (
    SCIMGroupCreate,
    SCIMGroupUpdate,
)

from app.services.scim.validation_service import (
    validate_group_payload,
)


class SCIMGroupService:
    """
    SCIM Group provisioning foundation.
    """

    def __init__(self) -> None:
        self._groups: dict[str, dict[str, Any]] = {}

    def create_group(
        self,
        payload: SCIMGroupCreate,
        tenant_id: str,
    ) -> dict[str, Any]:

        data = payload.model_dump(
            by_alias=True,
            exclude_none=True,
        )

        validate_group_payload(data)

        group_id = str(uuid4())

        resource = {
            "id": group_id,
            "tenant_id": tenant_id,
            **data,
            "meta": {
                "resourceType": "Group",
            },
        }

        self._groups[group_id] = resource

        return resource

    def list_groups(
        self,
        tenant_id: str,
    ) -> list[dict[str, Any]]:

        return [
            group
            for group in self._groups.values()
            if group["tenant_id"] == tenant_id
        ]

    def get_group(
        self,
        group_id: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:

        group = self._groups.get(group_id)

        if group is None:
            return None

        if group["tenant_id"] != tenant_id:
            return None

        return group

    def replace_group(
        self,
        group_id: str,
        payload: SCIMGroupUpdate,
        tenant_id: str,
    ) -> dict[str, Any] | None:

        existing = self.get_group(
            group_id,
            tenant_id,
        )

        if existing is None:
            return None

        data = payload.model_dump(
            by_alias=True,
            exclude_none=True,
        )

        validate_group_payload(data)

        existing.update(data)

        return existing

    def patch_group(
        self,
        group_id: str,
        operations: list[Any],
        tenant_id: str,
    ) -> dict[str, Any] | None:

        group = self.get_group(
            group_id,
            tenant_id,
        )

        if group is None:
            return None

        for operation in operations:
            operation_name = operation.op.lower()

            if operation_name in {
                "add",
                "replace",
            }:
                if operation.path:
                    group[operation.path] = operation.value

            elif operation_name == "remove":
                if operation.path:
                    group.pop(
                        operation.path,
                        None,
                    )

        return group

    def delete_group(
        self,
        group_id: str,
        tenant_id: str,
    ) -> bool:

        group = self.get_group(
            group_id,
            tenant_id,
        )

        if group is None:
            return False

        del self._groups[group_id]

        return True
