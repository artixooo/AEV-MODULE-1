from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.workspace import Workspace
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service layer for tenant-aware project operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_project(
        self,
        project_data: ProjectCreate,
    ) -> Project:
        """Create a project belonging to a workspace."""

        workspace = self.db.get(
            Workspace,
            project_data.workspace_id,
        )

        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )

        existing = (
            self.db.query(Project)
            .filter(
                Project.workspace_id == project_data.workspace_id,
                Project.project_code == project_data.project_code,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project code already exists in this workspace",
            )

        if (
            project_data.start_date is not None
            and project_data.end_date is not None
            and project_data.end_date < project_data.start_date
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project end date cannot be before start date",
            )

        project = Project(
            workspace_id=project_data.workspace_id,
            project_name=project_data.project_name,
            project_code=project_data.project_code,
            description=project_data.description,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            status=project_data.status,
        )

        self.db.add(project)

        try:
            self.db.commit()
            self.db.refresh(project)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project could not be created",
            )

        return project

    def get_project(
        self,
        project_id: UUID,
    ) -> Project:
        """Retrieve a project by ID."""

        project = self.db.get(
            Project,
            project_id,
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        return project

    def list_projects(
        self,
        workspace_id: UUID | None = None,
    ) -> list[Project]:
        """List projects, optionally scoped to a workspace."""

        query = self.db.query(Project)

        if workspace_id is not None:
            query = query.filter(
                Project.workspace_id == workspace_id,
            )

        return query.order_by(
            Project.project_name,
        ).all()

    def update_project(
        self,
        project_id: UUID,
        project_data: ProjectUpdate,
    ) -> Project:
        """Update a project."""

        project = self.get_project(project_id)

        update_data = project_data.model_dump(
            exclude_unset=True,
        )

        if (
            "start_date" in update_data
            and "end_date" in update_data
            and update_data["start_date"] is not None
            and update_data["end_date"] is not None
            and update_data["end_date"] < update_data["start_date"]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project end date cannot be before start date",
            )

        if "project_code" in update_data:
            existing = (
                self.db.query(Project)
                .filter(
                    Project.workspace_id == project.workspace_id,
                    Project.project_code == update_data["project_code"],
                    Project.id != project_id,
                )
                .first()
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Project code already exists "
                        "in this workspace"
                    ),
                )

        for field, value in update_data.items():
            setattr(project, field, value)

        try:
            self.db.commit()
            self.db.refresh(project)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project could not be updated",
            )

        return project

    def delete_project(
        self,
        project_id: UUID,
    ) -> None:
        """Delete a project."""

        project = self.get_project(project_id)

        self.db.delete(project)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project could not be deleted",
            )