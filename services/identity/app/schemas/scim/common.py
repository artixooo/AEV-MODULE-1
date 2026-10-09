from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


SCIM_USER_SCHEMA = (
    "urn:ietf:params:scim:schemas:core:2.0:User"
)

SCIM_GROUP_SCHEMA = (
    "urn:ietf:params:scim:schemas:core:2.0:Group"
)

SCIM_LIST_RESPONSE_SCHEMA = (
    "urn:ietf:params:scim:api:messages:2.0:ListResponse"
)

SCIM_ERROR_SCHEMA = (
    "urn:ietf:params:scim:api:messages:2.0:Error"
)


class SCIMBaseModel(BaseModel):
    """
    Base model for SCIM request/response schemas.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )


class SCIMErrorResponse(BaseModel):
    """
    Standard SCIM error response.
    """

    schemas: list[str] = Field(
        default_factory=lambda: [SCIM_ERROR_SCHEMA]
    )

    detail: str

    status: str


class SCIMListResponse(BaseModel):
    """
    Standard SCIM list response.
    """

    schemas: list[str] = Field(
        default_factory=lambda: [SCIM_LIST_RESPONSE_SCHEMA]
    )

    total_results: int

    start_index: int = 1

    items_per_page: int = 0

    resources: list[dict[str, Any]] = Field(
        default_factory=list
    )


class SCIMPatchOperation(BaseModel):
    """
    Individual SCIM PATCH operation.
    """

    op: str

    path: str | None = None

    value: Any = None


class SCIMPatchRequest(SCIMBaseModel):
    """
    SCIM PATCH request.

    The SCIM wire format uses 'Operations'.
    Python code uses 'operations'.
    """

    schemas: list[str]

    operations: list[SCIMPatchOperation] = Field(
        alias="Operations"
    )
