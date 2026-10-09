from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_context
from app.core.context import TenantContext
from app.db.database import get_db
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.services.workspace import WorkspaceService


router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"],
)


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create workspace",
)
def create_workspace(
    workspace_data: WorkspaceCreate,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Create a workspace."""

    service = WorkspaceService(db, context)

    return service.create_workspace(workspace_data)


@router.get(
    "",
    response_model=list[WorkspaceResponse],
    summary="List workspaces",
)
def list_workspaces(
    organization_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """List workspaces."""

    service = WorkspaceService(db, context)

    return service.list_workspaces(
        organization_id=organization_id,
    )


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Get workspace",
)
def get_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Get a workspace by ID."""

    service = WorkspaceService(db, context)

    return service.get_workspace(workspace_id)


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Update workspace",
)
def update_workspace(
    workspace_id: UUID,
    workspace_data: WorkspaceUpdate,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Update a workspace."""

    service = WorkspaceService(db, context)

    return service.update_workspace(
        workspace_id,
        workspace_data,
    )


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workspace",
)
def delete_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Delete a workspace."""

    service = WorkspaceService(db, context)

    service.delete_workspace(workspace_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )