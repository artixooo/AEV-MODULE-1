from fastapi import APIRouter

from app.schemas.oidc import OIDCProviderConfig
from app.services.oidc_service import OIDCService

router = APIRouter(
    prefix="/oidc",
    tags=["OpenID Connect"],
)


@router.post("/validate")
def validate_provider(config: OIDCProviderConfig):
    """Validate an OIDC provider configuration."""

    OIDCService.validate_issuer(config)

    return {
        "status": "valid",
        "provider": config.provider,
        "issuer": str(config.issuer),
        "discovery_url": OIDCService.get_discovery_url(config),
    }
