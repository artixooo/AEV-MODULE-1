from fastapi import Depends, Request

from app.core.context import TenantContext
from app.core.security import get_bearer_token, validate_jwt_claims


def get_current_context(
    request: Request,
    token: str = Depends(get_bearer_token),
) -> TenantContext:
    """
    Authenticate the request and construct the tenant context.
    """

    claims = validate_jwt_claims(token)

    context = TenantContext.from_claims(claims)

    request.state.authenticated_claims = claims
    request.state.tenant_context = context

    return context