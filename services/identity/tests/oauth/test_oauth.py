import pytest
from pydantic import ValidationError

from app.schemas.oauth import (
    OAuthAuthorizationRequest,
    OAuthCallbackRequest,
    OAuthProviderConfig,
)
from app.services.oauth_service import OAuthService


def valid_oauth_config():
    return OAuthProviderConfig(
        tenant_id="00000000-0000-0000-0000-000000000001",
        provider="example",
        client_id="client-123",
        client_secret_ref="secret/oauth/example/client-secret",
        authorization_url="https://provider.example.com/oauth/authorize",
        token_url="https://provider.example.com/oauth/token",
        redirect_uri="https://identity.example.com/oauth/callback",
        scopes=["openid", "profile", "email"],
    )


def test_valid_oauth_configuration():
    config = valid_oauth_config()

    assert config.provider == "example"
    assert config.client_id == "client-123"
    assert config.client_secret_ref.startswith("secret/")


def test_oauth_rejects_http_authorization_url():
    with pytest.raises(ValidationError):
        OAuthProviderConfig(
            provider="example",
            client_id="client-123",
            client_secret_ref="secret/oauth/example/client-secret",
            authorization_url="http://provider.example.com/oauth/authorize",
            token_url="https://provider.example.com/oauth/token",
            redirect_uri="https://identity.example.com/oauth/callback",
            scopes=["openid"],
        )


def test_oauth_rejects_empty_scopes():
    with pytest.raises(ValidationError):
        OAuthProviderConfig(
            provider="example",
            client_id="client-123",
            client_secret_ref="secret/oauth/example/client-secret",
            authorization_url="https://provider.example.com/oauth/authorize",
            token_url="https://provider.example.com/oauth/token",
            redirect_uri="https://identity.example.com/oauth/callback",
            scopes=[],
        )


def test_oauth_authorization_url():
    config = valid_oauth_config()

    request = OAuthAuthorizationRequest(
        provider="example",
        redirect_uri="https://identity.example.com/oauth/callback",
        state="1234567890abcdef",
        scopes=["openid", "email"],
    )

    url = OAuthService.build_authorization_url(config, request)

    assert url.startswith(
        "https://provider.example.com/oauth/authorize?"
    )
    assert "client_id=client-123" in url
    assert "response_type=code" in url
    assert "state=1234567890abcdef" in url


def test_oauth_callback_validation():
    callback = OAuthCallbackRequest(
        code="authorization-code",
        state="1234567890abcdef",
    )

    OAuthService.validate_callback(callback)


def test_oauth_callback_error():
    callback = OAuthCallbackRequest(
        code="authorization-code",
        state="1234567890abcdef",
        error="access_denied",
        error_description="User denied authorization",
    )

    with pytest.raises(ValueError, match="User denied authorization"):
        OAuthService.validate_callback(callback)


@pytest.mark.parametrize(
    "field",
    ["provider", "client_id", "client_secret_ref"],
)
def test_oauth_required_fields(field):
    data = {
        "tenant_id": "00000000-0000-0000-0000-000000000001",
        "provider": "example",
        "client_id": "client-123",
        "client_secret_ref": "secret/oauth/example/client-secret",
        "authorization_url": "https://provider.example.com/oauth/authorize",
        "token_url": "https://provider.example.com/oauth/token",
        "redirect_uri": "https://identity.example.com/oauth/callback",
        "scopes": ["openid", "profile", "email"],
    }

    data.pop(field)

    with pytest.raises(ValidationError):
        OAuthProviderConfig(**data)


@pytest.mark.parametrize(
    "field",
    ["authorization_url", "token_url", "redirect_uri"],
)
def test_oauth_rejects_http_urls(field):
    data = {
        "tenant_id": "00000000-0000-0000-0000-000000000001",
        "provider": "example",
        "client_id": "client-123",
        "client_secret_ref": "secret/oauth/example/client-secret",
        "authorization_url": "https://provider.example.com/oauth/authorize",
        "token_url": "https://provider.example.com/oauth/token",
        "redirect_uri": "https://identity.example.com/oauth/callback",
        "scopes": ["openid", "profile", "email"],
    }

    data[field] = "http://provider.example.com/insecure"

    with pytest.raises(ValidationError):
        OAuthProviderConfig(**data)


def test_oauth_callback_rejects_short_state():
    with pytest.raises(ValidationError):
        OAuthCallbackRequest(
            code="authorization-code",
            state="short",
        )


def test_oauth_callback_requires_code():
    with pytest.raises(ValidationError):
        OAuthCallbackRequest(
            state="1234567890abcdef",
        )
