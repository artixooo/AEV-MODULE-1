from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.context import TenantContext
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.workspace import Workspace
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class OrganizationService:
    """Service layer for Organization management operations."""

    def __init__(self, db: Session, context: TenantContext):
        self.db = db
        self.context = context

    def get_status(self) -> dict:
        """Return service readiness status."""
        return {"status": "OrganizationService initialized"}

    def _require_tenant_context(self) -> None:
        """Require an authenticated tenant context."""
        if not self.context.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant context is required",
            )

    def _get_authenticated_user_id(self) -> UUID:
        """Return authenticated user ID as UUID."""
        try:
            return UUID(str(self.context.user_id))
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authenticated user ID",
            )

    def _require_organization_membership(
        self,
        organization_id: UUID,
    ) -> Membership:
        """Require an active membership for the authenticated user."""
        user_id = self._get_authenticated_user_id()

        membership = (
            self.db.query(Membership)
            .filter(
                Membership.user_id == user_id,
                Membership.organization_id == organization_id,
                Membership.membership_status == "ACTIVE",
            )
            .first()
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not an active member of this organization",
            )

        return membership

    def create_organization(
        self,
        organization_data: OrganizationCreate,
    ) -> Organization:
        """Create a new organization."""

        self._require_tenant_context()

        if organization_data.parent_organization_id:
            parent = self.db.get(
                Organization,
                organization_data.parent_organization_id,
            )

            if parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent organization not found",
                )

            self._require_organization_membership(parent.id)

        existing = (
            self.db.query(Organization)
            .filter(
                Organization.organization_code
                == organization_data.organization_code
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization code already exists",
            )

        organization = Organization(
            organization_name=organization_data.organization_name,
            organization_code=organization_data.organization_code,
            description=organization_data.description,
            website=organization_data.website,
            status=organization_data.status,
            parent_organization_id=(
                organization_data.parent_organization_id
            ),
        )

        self.db.add(organization)

        try:
            self.db.commit()
            self.db.refresh(organization)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization could not be created",
            )

        return organization

    def get_organization(
        self,
        organization_id: UUID,
    ) -> Organization:
        """Retrieve an organization by ID."""

        self._require_tenant_context()

        organization = self.db.get(
            Organization,
            organization_id,
        )

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        self._require_organization_membership(organization.id)

        return organization

    def list_organizations(
        self,
        parent_organization_id: Optional[UUID] = None,
    ) -> list[Organization]:
        """List organizations visible to the authenticated user."""

        self._require_tenant_context()

        user_id = self._get_authenticated_user_id()

        query = (
            self.db.query(Organization)
            .join(
                Membership,
                Membership.organization_id == Organization.id,
            )
            .filter(
                Membership.user_id == user_id,
                Membership.membership_status == "ACTIVE",
            )
        )

        if parent_organization_id is not None:
            query = query.filter(
                Organization.parent_organization_id
                == parent_organization_id
            )

        return query.order_by(
            Organization.organization_name
        ).all()

    def update_organization(
        self,
        organization_id: UUID,
        organization_data: OrganizationUpdate,
    ) -> Organization:
        """Update an existing organization."""

        self._require_tenant_context()

        organization = self.get_organization(organization_id)

        if (
            organization_data.organization_code is not None
            and organization_data.organization_code
            != organization.organization_code
        ):
            existing = (
                self.db.query(Organization)
                .filter(
                    Organization.organization_code
                    == organization_data.organization_code,
                    Organization.id != organization_id,
                )
                .first()
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Organization code already exists",
                )

        if organization_data.parent_organization_id is not None:
            if (
                organization_data.parent_organization_id
                == organization_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization cannot be its own parent",
                )

            parent = self.db.get(
                Organization,
                organization_data.parent_organization_id,
            )

            if parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent organization not found",
                )

            self._require_organization_membership(parent.id)

        update_data = organization_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(organization, field, value)

        try:
            self.db.commit()
            self.db.refresh(organization)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization could not be updated",
            )

        return organization

    def delete_organization(
        self,
        organization_id: UUID,
    ) -> None:
        """Delete an organization."""

        self._require_tenant_context()

        organization = self.get_organization(organization_id)

        self.db.delete(organization)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Organization could not be deleted",
            )