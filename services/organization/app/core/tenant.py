from fastapi import HTTPException, status

from app.core.context import TenantContext


def require_tenant_context(context: TenantContext) -> str:
    """
    Return the authenticated tenant_id.

    The tenant_id comes only from the authenticated JWT context.
    Client-supplied tenant identifiers must not be used here.
    """
    tenant_id = context.tenant_id

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated tenant context is required",
        )

    return tenant_id
