from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SCIM_CONFIGURATION_STATUSES = {
    "active",
    "inactive",
    "disabled",
}


class SCIMConfigurationBase(BaseModel):
    """
    Base API schema for tenant-scoped SCIM configuration.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    tenant_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Tenant associated with this SCIM configuration.",
    )

    enabled: bool = Field(
        default=True,
        description="Whether SCIM is enabled for the tenant.",
    )

    endpoint: str = Field(
        default="/scim/v2",
        min_length=1,
        max_length=255,
        description="Base SCIM endpoint for the tenant.",
    )

    provisioning_enabled: bool = Field(
        default=True,
        description="Whether SCIM user and group provisioning is enabled.",
    )

    status: Literal[
        "active",
        "inactive",
        "disabled",
    ] = Field(
        default="active",
        description="Current status of the SCIM configuration.",
    )

    @field_validator("tenant_id")
    @classmethod
    def validate_tenant_id(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("tenant_id cannot be empty")

        return value

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, value: str) -> str:
        value = value.strip()

        if not value.startswith("/"):
            raise ValueError("SCIM endpoint must start with '/'")

        if not value.startswith("/scim"):
            raise ValueError(
                "SCIM endpoint must be under the '/scim' path"
            )

        return value


class SCIMConfigurationCreate(SCIMConfigurationBase):
    """
    Request schema for creating SCIM configuration.
    """

    pass


class SCIMConfigurationResponse(SCIMConfigurationBase):
    """
    Response schema for SCIM configuration.
    """

    pass