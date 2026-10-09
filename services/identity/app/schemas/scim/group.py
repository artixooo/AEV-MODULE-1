from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.scim.common import SCIM_GROUP_SCHEMA


class SCIMGroupMember(BaseModel):
    """
    SCIM Group member.
    """

    value: str

    display: str | None = None

    type: str = "User"


class SCIMGroupCreate(BaseModel):
    """
    SCIM Group creation request.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    schemas: list[str] = Field(
        default_factory=lambda: [SCIM_GROUP_SCHEMA]
    )

    display_name: str = Field(
        ...,
        alias="displayName",
        min_length=1,
        max_length=255,
    )

    members: list[SCIMGroupMember] = Field(
        default_factory=list
    )


class SCIMGroupUpdate(SCIMGroupCreate):
    """
    SCIM Group replacement request.
    """

    pass


class SCIMGroupResponse(SCIMGroupCreate):
    """
    SCIM Group response.
    """

    id: str

    meta: dict = Field(
        default_factory=dict
    )
