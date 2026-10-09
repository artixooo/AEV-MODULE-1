from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_context
from app.core.context import TenantContext
from app.db.database import get_db
from app.schemas.membership import (
    MembershipCreate,
    MembershipResponse,
    MembershipUpdate,
)
from app.services.membership import MembershipService


router = APIRouter(
    prefix="/memberships",
    tags=["Memberships"],
)


@router.post(
    "",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create membership",
)
def create_membership(
    membership_data: MembershipCreate,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Create a membership."""

    service = MembershipService(db, context)

    return service.create_membership(membership_data)


@router.get(
    "",
    response_model=list[MembershipResponse],
    summary="List memberships",
)
def list_memberships(
    organization_id: Optional[UUID] = Query(default=None),
    workspace_id: Optional[UUID] = Query(default=None),
    user_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """List memberships."""

    service = MembershipService(db, context)

    return service.list_memberships(
        organization_id=organization_id,
        workspace_id=workspace_id,
        user_id=user_id,
    )


@router.get(
    "/{membership_id}",
    response_model=MembershipResponse,
    summary="Get membership",
)
def get_membership(
    membership_id: UUID,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Get a membership by ID."""

    service = MembershipService(db, context)

    return service.get_membership(membership_id)


@router.patch(
    "/{membership_id}",
    response_model=MembershipResponse,
    summary="Update membership",
)
def update_membership(
    membership_id: UUID,
    membership_data: MembershipUpdate,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Update membership."""

    service = MembershipService(db, context)

    return service.update_membership(
        membership_id,
        membership_data,
    )


@router.delete(
    "/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete membership",
)
def delete_membership(
    membership_id: UUID,
    db: Session = Depends(get_db),
    context: TenantContext = Depends(get_current_context),
):
    """Delete a membership."""

    service = MembershipService(db, context)

    service.delete_membership(membership_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)