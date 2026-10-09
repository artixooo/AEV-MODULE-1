from app.schemas.oidc import (
    OIDCDiscoveryDocument,
    OIDCProviderConfig,
)


class OIDCService:
    """OpenID Connect integration interface."""

    @staticmethod
    def get_discovery_url(
        config: OIDCProviderConfig,
    ) -> str:
        """Return the configured discovery document URL."""

        if config.discovery_url:
            return str(config.discovery_url)

        return f"{str(config.issuer).rstrip('/')}/.well-known/openid-configuration"

    @staticmethod
    def validate_issuer(config: OIDCProviderConfig) -> None:
        """Validate the OIDC issuer configuration."""

        if config.issuer.scheme != "https":
            raise ValueError("OIDC issuer must use HTTPS")

        if not str(config.issuer).rstrip("/"):
            raise ValueError("OIDC issuer cannot be empty")

    @staticmethod
    def validate_discovery_document(
        document: OIDCDiscoveryDocument,
        config: OIDCProviderConfig,
    ) -> None:
        """Validate that discovery belongs to the configured issuer."""

        configured_issuer = str(config.issuer).rstrip("/")
        discovered_issuer = str(document.issuer).rstrip("/")

        if configured_issuer != discovered_issuer:
            raise ValueError(
                "OIDC discovery issuer does not match configured issuer"
            )
