from typing import List
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator


class OAuthProviderConfig(BaseModel):
    tenant_id: UUID
    """OAuth 2.0 provider configuration."""

    provider: str = Field(..., min_length=1, max_length=100)
    client_id: str = Field(..., min_length=1, max_length=255)

    # Reference to a secret managed outside the Identity Service.
    client_secret_ref: str = Field(..., min_length=1, max_length=255)

    authorization_url: AnyHttpUrl
    token_url: AnyHttpUrl
    redirect_uri: AnyHttpUrl

    scopes: List[str] = Field(
        default_factory=lambda: ["openid", "profile", "email"]
    )

    @field_validator("authorization_url", "token_url", "redirect_uri")
    @classmethod
    def validate_https_url(cls, value):
        if value.scheme != "https":
            raise ValueError("OAuth URLs must use HTTPS")
        return value

    @field_validator("scopes")
    @classmethod
    def validate_scopes(cls, value):
        if not value:
            raise ValueError("At least one OAuth scope is required")

        cleaned = [scope.strip() for scope in value]

        if any(not scope for scope in cleaned):
            raise ValueError("OAuth scopes cannot be empty")

        return cleaned


class OAuthAuthorizationRequest(BaseModel):
    """Parameters required to start an OAuth authorization flow."""

    provider: str = Field(..., min_length=1, max_length=100)
    redirect_uri: AnyHttpUrl
    state: str = Field(..., min_length=16, max_length=512)
    scopes: List[str] = Field(default_factory=list)


class OAuthCallbackRequest(BaseModel):
    """OAuth callback parameters returned by the provider."""

    code: str = Field(..., min_length=1)
    state: str = Field(..., min_length=16, max_length=512)
    error: str | None = None
    error_description: str | None = None


class OAuthTokenResponse(BaseModel):
    """Normalized OAuth token response."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int | None = None
    refresh_token: str | None = None
    scope: str | None = None
