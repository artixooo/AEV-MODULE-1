from typing import List
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator


class OIDCProviderConfig(BaseModel):
    tenant_id: UUID
    """OpenID Connect provider configuration."""

    provider: str = Field(..., min_length=1, max_length=100)
    issuer: AnyHttpUrl
    client_id: str = Field(..., min_length=1, max_length=255)

    # Reference to a secret managed outside the Identity Service.
    client_secret_ref: str = Field(..., min_length=1, max_length=255)

    redirect_uri: AnyHttpUrl

    scopes: List[str] = Field(
        default_factory=lambda: ["openid", "profile", "email"]
    )

    discovery_url: AnyHttpUrl | None = None

    @field_validator("issuer", "redirect_uri", "discovery_url")
    @classmethod
    def validate_https_url(cls, value):
        if value is None:
            return value

        if value.scheme != "https":
            raise ValueError("OIDC URLs must use HTTPS")

        return value

    @field_validator("scopes")
    @classmethod
    def validate_openid_scope(cls, value):
        if "openid" not in value:
            raise ValueError("OIDC configuration must include the openid scope")

        return value


class OIDCDiscoveryDocument(BaseModel):
    """OIDC discovery document interface."""

    issuer: AnyHttpUrl
    authorization_endpoint: AnyHttpUrl
    token_endpoint: AnyHttpUrl
    userinfo_endpoint: AnyHttpUrl | None = None
    jwks_uri: AnyHttpUrl

    @field_validator(
        "issuer",
        "authorization_endpoint",
        "token_endpoint",
        "userinfo_endpoint",
        "jwks_uri",
    )
    @classmethod
    def validate_https_url(cls, value):
        if value is None:
            return value

        if value.scheme != "https":
            raise ValueError("OIDC discovery URLs must use HTTPS")

        return value
