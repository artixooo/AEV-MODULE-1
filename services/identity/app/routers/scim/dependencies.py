from fastapi import Depends, HTTPException, status

from app.utils.jwt import verify_token


def get_current_tenant(
    payload: dict = Depends(verify_token),
) -> str:
    tenant_id = payload.get("tenant_id")

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated tenant context is required.",
        )

    return str(tenant_id)  
