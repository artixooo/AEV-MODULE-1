from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_context
from app.core.context import TenantContext
from app.db.database import get_db
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.services.organization import OrganizationService


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
)
def create_organization(
    organization_data: OrganizationCreate,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Create a new organization."""

    service = OrganizationService(db, context)

    return service.create_organization(organization_data)


@router.get(
    "",
    response_model=list[OrganizationResponse],
    summary="List organizations",
)
def list_organizations(
    parent_organization_id: Optional[UUID] = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """List organizations."""

    service = OrganizationService(db, context)

    return service.list_organizations(
        parent_organization_id=parent_organization_id,
    )


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Get organization",
)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Get an organization by ID."""

    service = OrganizationService(db, context)

    return service.get_organization(organization_id)


@router.patch(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Update organization",
)
def update_organization(
    organization_id: UUID,
    organization_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Update an organization."""

    service = OrganizationService(db, context)

    return service.update_organization(
        organization_id,
        organization_data,
    )


@router.delete(
    "/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete organization",
)
def delete_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Delete an organization."""

    service = OrganizationService(db, context)

    service.delete_organization(organization_id)

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )