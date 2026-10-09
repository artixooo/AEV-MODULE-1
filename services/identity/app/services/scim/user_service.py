from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.schemas.scim.user import (
    SCIMUserCreate,
    SCIMUserUpdate,
)

from app.services.scim.validation_service import (
    validate_user_payload,
)


class SCIMUserService:
    """
    SCIM User provisioning foundation.

    This implementation intentionally provides the API/service
    foundation. Persistence should later be connected to the
    existing Identity Service repository layer.
    """

    def __init__(self) -> None:
        self._users: dict[str, dict[str, Any]] = {}

    def create_user(
        self,
        payload: SCIMUserCreate,
        tenant_id: str,
    ) -> dict[str, Any]:

        data = payload.model_dump(
            by_alias=True,
            exclude_none=True,
        )

        validate_user_payload(data)

        user_id = str(uuid4())

        resource = {
            "id": user_id,
            "tenant_id": tenant_id,
            **data,
            "meta": {
                "resourceType": "User",
            },
        }

        self._users[user_id] = resource

        return resource

    def list_users(
        self,
        tenant_id: str,
    ) -> list[dict[str, Any]]:

        return [
            user
            for user in self._users.values()
            if user["tenant_id"] == tenant_id
        ]

    def get_user(
        self,
        user_id: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:

        user = self._users.get(user_id)

        if user is None:
            return None

        if user["tenant_id"] != tenant_id:
            return None

        return user

    def replace_user(
        self,
        user_id: str,
        payload: SCIMUserUpdate,
        tenant_id: str,
    ) -> dict[str, Any] | None:

        existing = self.get_user(
            user_id,
            tenant_id,
        )

        if existing is None:
            return None

        data = payload.model_dump(
            by_alias=True,
            exclude_none=True,
        )

        validate_user_payload(data)

        existing.update(data)

        return existing

    def patch_user(
        self,
        user_id: str,
        operations: list[Any],
        tenant_id: str,
    ) -> dict[str, Any] | None:

        user = self.get_user(
            user_id,
            tenant_id,
        )

        if user is None:
            return None

        for operation in operations:
            operation_name = operation.op.lower()

            if operation_name in {
                "add",
                "replace",
            }:
                if operation.path:
                    user[operation.path] = operation.value

            elif operation_name == "remove":
                if operation.path:
                    user.pop(
                        operation.path,
                        None,
                    )

        return user

    def delete_user(
        self,
        user_id: str,
        tenant_id: str,
    ) -> bool:

        user = self.get_user(
            user_id,
            tenant_id,
        )

        if user is None:
            return False

        del self._users[user_id]

        return True
