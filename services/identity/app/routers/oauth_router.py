from fastapi import APIRouter, HTTPException

from app.schemas.oauth import (
    OAuthAuthorizationRequest,
    OAuthCallbackRequest,
    OAuthProviderConfig,
)
from app.services.oauth_service import OAuthService

router = APIRouter(
    prefix="/oauth",
    tags=["OAuth 2.0"],
)


@router.post("/authorize")
def authorize(request: OAuthAuthorizationRequest):
    """
    Build an OAuth 2.0 authorization URL.

    Provider configuration will eventually be loaded from
    configuration/secrets infrastructure.
    """

    raise HTTPException(
        status_code=501,
        detail="OAuth provider configuration integration is not enabled yet",
    )


@router.post("/callback")
def callback(request: OAuthCallbackRequest):
    """Validate an OAuth provider callback."""

    try:
        OAuthService.validate_callback(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "status": "callback_received",
        "message": "OAuth callback validated successfully",
    }
