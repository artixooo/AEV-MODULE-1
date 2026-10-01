"""
Service-to-Service Authorization Middleware.

Per the Gateway team's authentication-contract.md (branch
week-3-gateway-auth): the target architecture has the Gateway
validate end-user JWTs and extract tenant_id/roles/permissions
claims before forwarding requests downstream. Identity Service does
not issue those claims yet, and Gateway's own JWT middleware has not
merged into develop.

Until that lands, this service cannot safely trust a role_code
supplied by an arbitrary end-user's JWT for POST /evaluate — nothing
proves the caller actually holds that role. Rather than build a
JWT-based authorization check against claims that don't exist yet,
/evaluate is restricted to trusted internal callers (Gateway, or any
other backend service acting on a user's behalf after it has
established their real role) via a shared service credential, sent
as X-Service-API-Key.

This is the "restrict this endpoint to internal policy-evaluation
usage" option from the #61 review, chosen because a real JWT-based
role mapping isn't buildable until Identity Service adds it.

Author: Utkarsh Pratham (Squad Lead) & Narayanan Varadarajan
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

from fastapi import Header, HTTPException

from app.core.config import settings


def require_service_credential(x_service_api_key: str = Header(...)):
    """
    FastAPI dependency: verifies the caller presents the shared
    internal service credential.

    Raises:
        HTTPException(403) if the credential is missing or wrong.
    """
    if x_service_api_key != settings.SERVICE_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing service credential")
    return True