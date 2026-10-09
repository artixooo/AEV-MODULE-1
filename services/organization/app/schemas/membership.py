from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MembershipBase(BaseModel):
    user_id: UUID
    organization_id: UUID
    workspace_id: UUID
    membership_status: str = Field(
        default="ACTIVE",
        max_length=30,
    )


class MembershipCreate(MembershipBase):
    pass


class MembershipUpdate(BaseModel):
    membership_status: str | None = Field(
        default=None,
        max_length=30,
    )


class MembershipResponse(MembershipBase):
    id: UUID
    joined_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)