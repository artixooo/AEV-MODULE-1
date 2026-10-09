from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceBase(BaseModel):
    organization_id: UUID
    workspace_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )
    workspace_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )
    description: str | None = None
    status: str = Field(
        default="ACTIVE",
        max_length=30,
    )


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    workspace_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    workspace_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    description: str | None = None
    status: str | None = Field(
        default=None,
        max_length=30,
    )


class WorkspaceResponse(WorkspaceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)