from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.models.organization import Organization
from app.models.workspace import Workspace
from app.schemas.membership import (
    MembershipCreate,
    MembershipUpdate,
)


class MembershipService:
    """Service layer for tenant-aware membership operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_membership(
        self,
        membership_data: MembershipCreate,
    ) -> Membership:
        """Create a membership after validating organization/workspace ownership."""

        organization = self.db.get(
            Organization,
            membership_data.organization_id,
        )

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        workspace = self.db.get(
            Workspace,
            membership_data.workspace_id,
        )

        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )

        if workspace.organization_id != membership_data.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace does not belong to the organization",
            )

        existing = (
            self.db.query(Membership)
            .filter(
                Membership.user_id == membership_data.user_id,
                Membership.organization_id
                == membership_data.organization_id,
                Membership.workspace_id
                == membership_data.workspace_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Membership already exists",
            )

        membership = Membership(
            user_id=membership_data.user_id,
            organization_id=membership_data.organization_id,
            workspace_id=membership_data.workspace_id,
            membership_status=membership_data.membership_status,
        )

        self.db.add(membership)

        try:
            self.db.commit()
            self.db.refresh(membership)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Membership could not be created",
            )

        return membership

    def get_membership(
        self,
        membership_id: UUID,
    ) -> Membership:
        """Retrieve a membership by ID."""

        membership = self.db.get(
            Membership,
            membership_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found",
            )

        return membership

    def list_memberships(
        self,
        organization_id: UUID | None = None,
        workspace_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> list[Membership]:
        """List memberships using optional filters."""

        query = self.db.query(Membership)

        if organization_id is not None:
            query = query.filter(
                Membership.organization_id == organization_id,
            )

        if workspace_id is not None:
            query = query.filter(
                Membership.workspace_id == workspace_id,
            )

        if user_id is not None:
            query = query.filter(
                Membership.user_id == user_id,
            )

        return query.order_by(
            Membership.created_at,
        ).all()

    def update_membership(
        self,
        membership_id: UUID,
        membership_data: MembershipUpdate,
    ) -> Membership:
        """Update membership status."""

        membership = self.get_membership(membership_id)

        update_data = membership_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(membership, field, value)

        try:
            self.db.commit()
            self.db.refresh(membership)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Membership could not be updated",
            )

        return membership

    def delete_membership(
        self,
        membership_id: UUID,
    ) -> None:
        """Delete a membership."""

        membership = self.get_membership(membership_id)

        self.db.delete(membership)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Membership could not be deleted",
            )