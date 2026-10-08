from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationBase(BaseModel):
    organization_name: str = Field(..., min_length=1, max_length=255)
    organization_code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    website: Optional[str] = Field(default=None, max_length=255)
    status: str = Field(default="ACTIVE", max_length=30)


class OrganizationCreate(OrganizationBase):
    parent_organization_id: Optional[UUID] = None


class OrganizationUpdate(BaseModel):
    organization_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    organization_code: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    description: Optional[str] = None
    website: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    status: Optional[str] = Field(
        default=None,
        max_length=30,
    )
    parent_organization_id: Optional[UUID] = None


class OrganizationResponse(OrganizationBase):
    id: UUID
    parent_organization_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenantQuotaBase(BaseModel):
    quota_name: str
    limit_value: int
    unit: str
    description: Optional[str] = None


class TenantQuotaCreate(TenantQuotaBase):
    pass


class TenantQuotaUpdate(BaseModel):
    quota_name: Optional[str] = None
    limit_value: Optional[int] = None
    unit: Optional[str] = None
    description: Optional[str] = None


class TenantQuotaResponse(TenantQuotaBase):
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
