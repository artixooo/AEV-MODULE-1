from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_context
from app.core.context import TenantContext
from app.db.database import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    service = ProjectService(db, context)
    return service.create_project(project_data)


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    workspace_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    service = ProjectService(db, context)
    return service.list_projects(workspace_id=workspace_id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    service = ProjectService(db, context)
    return service.get_project(project_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    service = ProjectService(db, context)
    return service.update_project(project_id, project_data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    service = ProjectService(db, context)
    service.delete_project(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
