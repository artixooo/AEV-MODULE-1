from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class WorkspaceService:
    """Service layer for tenant-aware workspace operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_workspace(
        self,
        workspace_data: WorkspaceCreate,
    ) -> Workspace:
        """Create a workspace belonging to an organization."""

        organization = self.db.get(
            Organization,
            workspace_data.organization_id,
        )

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        existing = (
            self.db.query(Workspace)
            .filter(
                Workspace.organization_id
                == workspace_data.organization_id,
                Workspace.workspace_code
                == workspace_data.workspace_code,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Workspace code already exists in this organization",
            )

        workspace = Workspace(
            organization_id=workspace_data.organization_id,
            workspace_name=workspace_data.workspace_name,
            workspace_code=workspace_data.workspace_code,
            description=workspace_data.description,
            status=workspace_data.status,
        )

        self.db.add(workspace)

        try:
            self.db.commit()
            self.db.refresh(workspace)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Workspace could not be created",
            )

        return workspace

    def get_workspace(
        self,
        workspace_id: UUID,
    ) -> Workspace:
        """Retrieve a workspace by ID."""

        workspace = self.db.get(
            Workspace,
            workspace_id,
        )

        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )

        return workspace

    def list_workspaces(
        self,
        organization_id: UUID | None = None,
    ) -> list[Workspace]:
        """List workspaces, optionally scoped to an organization."""

        query = self.db.query(Workspace)

        if organization_id is not None:
            query = query.filter(
                Workspace.organization_id == organization_id,
            )

        return query.order_by(
            Workspace.workspace_name,
        ).all()

    def update_workspace(
        self,
        workspace_id: UUID,
        workspace_data: WorkspaceUpdate,
    ) -> Workspace:
        """Update a workspace."""

        workspace = self.get_workspace(workspace_id)

        update_data = workspace_data.model_dump(
            exclude_unset=True,
        )

        if "workspace_code" in update_data:
            existing = (
                self.db.query(Workspace)
                .filter(
                    Workspace.organization_id
                    == workspace.organization_id,
                    Workspace.workspace_code
                    == update_data["workspace_code"],
                    Workspace.id != workspace_id,
                )
                .first()
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Workspace code already exists "
                        "in this organization"
                    ),
                )

        for field, value in update_data.items():
            setattr(workspace, field, value)

        try:
            self.db.commit()
            self.db.refresh(workspace)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Workspace could not be updated",
            )

        return workspace

    def delete_workspace(
        self,
        workspace_id: UUID,
    ) -> None:
        """Delete a workspace."""

        workspace = self.get_workspace(workspace_id)

        self.db.delete(workspace)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Workspace could not be deleted",
            )