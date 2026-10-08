from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.context import TenantContext
from app.core.tenant import require_tenant_context
from app.db.database import get_db
from app.models.quota import TenantQuota
from app.schemas.organization import (
    TenantQuotaCreate,
    TenantQuotaResponse,
    TenantQuotaUpdate,
)

router = APIRouter(prefix="/quotas", tags=["Tenant Quotas"])


def get_tenant_id(context: TenantContext = Depends()) -> str:
    return require_tenant_context(context)


@router.post(
    "",
    response_model=TenantQuotaResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_quota(
    payload: TenantQuotaCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    quota = TenantQuota(
        tenant_id=tenant_id,
        quota_name=payload.quota_name,
        limit_value=payload.limit_value,
        unit=payload.unit,
        description=payload.description,
    )
    db.add(quota)
    db.commit()
    db.refresh(quota)
    return quota


@router.get("", response_model=list[TenantQuotaResponse])
def list_quotas(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    return (
        db.query(TenantQuota)
        .filter(TenantQuota.tenant_id == tenant_id)
        .all()
    )


@router.get("/{quota_id}", response_model=TenantQuotaResponse)
def get_quota(
    quota_id: UUID,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    quota = (
        db.query(TenantQuota)
        .filter(
            TenantQuota.id == quota_id,
            TenantQuota.tenant_id == tenant_id,
        )
        .first()
    )

    if not quota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quota not found",
        )

    return quota


@router.put("/{quota_id}", response_model=TenantQuotaResponse)
def update_quota(
    quota_id: UUID,
    payload: TenantQuotaUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    quota = (
        db.query(TenantQuota)
        .filter(
            TenantQuota.id == quota_id,
            TenantQuota.tenant_id == tenant_id,
        )
        .first()
    )

    if not quota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quota not found",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(quota, field, value)

    db.commit()
    db.refresh(quota)
    return quota


@router.delete("/{quota_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quota(
    quota_id: UUID,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    quota = (
        db.query(TenantQuota)
        .filter(
            TenantQuota.id == quota_id,
            TenantQuota.tenant_id == tenant_id,
        )
        .first()
    )

    if not quota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quota not found",
        )

    db.delete(quota)
    db.commit()
