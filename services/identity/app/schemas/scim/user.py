from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.scim.common import SCIM_USER_SCHEMA


class SCIMName(BaseModel):
    """
    SCIM User name structure.
    """

    given_name: str | None = Field(
        default=None,
        alias="givenName",
    )

    family_name: str | None = Field(
        default=None,
        alias="familyName",
    )

    formatted: str | None = None

    model_config = ConfigDict(
        populate_by_name=True,
    )


class SCIMEmail(BaseModel):
    """
    SCIM email structure.

    Email is kept as a string so this foundation does not require
    an additional email-validation dependency.
    """

    value: str

    type: str | None = None

    primary: bool = False


class SCIMUserCreate(BaseModel):
    """
    SCIM User creation request.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    schemas: list[str] = Field(
        default_factory=lambda: [SCIM_USER_SCHEMA]
    )

    user_name: str = Field(
        ...,
        alias="userName",
        min_length=1,
        max_length=255,
    )

    active: bool = True

    name: SCIMName | None = None

    emails: list[SCIMEmail] = Field(
        default_factory=list
    )


class SCIMUserUpdate(SCIMUserCreate):
    """
    SCIM User replacement request.
    """

    pass


class SCIMUserResponse(SCIMUserCreate):
    """
    SCIM User response.
    """

    id: str

    meta: dict = Field(
        default_factory=dict
    )
