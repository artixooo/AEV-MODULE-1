from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    workspace_id: UUID
    project_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )
    project_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = Field(
        default="PLANNING",
        max_length=30,
    )


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    project_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = Field(
        default=None,
        max_length=30,
    )


class ProjectResponse(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)