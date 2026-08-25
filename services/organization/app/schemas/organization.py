from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationBase(BaseModel):
    organization_name: str
    organization_code: str
    description: Optional[str] = None
    website: Optional[str] = None
    status: str = "ACTIVE"


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    organization_name: Optional[str] = None
    organization_code: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)