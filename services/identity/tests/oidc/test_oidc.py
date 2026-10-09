import pytest
from pydantic import ValidationError

from app.schemas.oidc import OIDCDiscoveryDocument, OIDCProviderConfig
from app.services.oidc_service import OIDCService


def valid_oidc_config():
    return OIDCProviderConfig(
        tenant_id="00000000-0000-0000-0000-000000000001",
        provider="example",
        issuer="https://accounts.example.com",
        client_id="client-123",
        client_secret_ref="secret/oidc/example/client-secret",
        redirect_uri="https://identity.example.com/oidc/callback",
        scopes=["openid", "profile", "email"],
    )


def test_valid_oidc_configuration():
    config = valid_oidc_config()

    assert config.provider == "example"
    assert str(config.issuer) == "https://accounts.example.com/"


def test_oidc_requires_openid_scope():
    with pytest.raises(ValidationError):
        OIDCProviderConfig(
            provider="example",
            issuer="https://accounts.example.com",
            client_id="client-123",
            client_secret_ref="secret/oidc/example/client-secret",
            redirect_uri="https://identity.example.com/oidc/callback",
            scopes=["profile", "email"],
        )


def test_oidc_rejects_http_issuer():
    with pytest.raises(ValidationError):
        OIDCProviderConfig(
            provider="example",
            issuer="http://accounts.example.com",
            client_id="client-123",
            client_secret_ref="secret/oidc/example/client-secret",
            redirect_uri="https://identity.example.com/oidc/callback",
            scopes=["openid"],
        )


def test_oidc_discovery_url():
    config = valid_oidc_config()

    discovery_url = OIDCService.get_discovery_url(config)

    assert discovery_url == (
        "https://accounts.example.com/"
        ".well-known/openid-configuration"
    )


def test_oidc_issuer_validation():
    config = valid_oidc_config()

    OIDCService.validate_issuer(config)


def test_oidc_secret_is_reference():
    config = valid_oidc_config()

    assert "client_secret" not in config.model_dump()
    assert config.client_secret_ref.startswith("secret/")


@pytest.mark.parametrize(
    "field",
    ["provider", "issuer", "client_id", "client_secret_ref"],
)
def test_oidc_required_fields(field):
    data = {
        "tenant_id": "00000000-0000-0000-0000-000000000001",
        "provider": "example",
        "issuer": "https://issuer.example.com",
        "client_id": "client-123",
        "client_secret_ref": "secret/oidc/example/client-secret",
        "redirect_uri": "https://identity.example.com/oidc/callback",
        "scopes": ["openid", "profile", "email"],
    }

    data.pop(field)

    with pytest.raises(ValidationError):
        OIDCProviderConfig(**data)


@pytest.mark.parametrize(
    "field",
    ["issuer", "redirect_uri", "discovery_url"],
)
def test_oidc_rejects_http_urls(field):
    data = {
        "tenant_id": "00000000-0000-0000-0000-000000000001",
        "provider": "example",
        "issuer": "https://issuer.example.com",
        "client_id": "client-123",
        "client_secret_ref": "secret/oidc/example/client-secret",
        "redirect_uri": "https://identity.example.com/oidc/callback",
        "scopes": ["openid", "profile", "email"],
        "discovery_url": "https://issuer.example.com/.well-known/openid-configuration",
    }

    data[field] = "http://issuer.example.com/insecure"

    with pytest.raises(ValidationError):
        OIDCProviderConfig(**data)


def test_oidc_discovery_issuer_mismatch():
    config = valid_oidc_config()

    document = OIDCDiscoveryDocument(
        issuer="https://different.example.com",
        authorization_endpoint="https://issuer.example.com/oauth/authorize",
        token_endpoint="https://issuer.example.com/oauth/token",
        jwks_uri="https://issuer.example.com/.well-known/jwks.json",
    )

    with pytest.raises(ValueError, match="does not match"):
        OIDCService.validate_discovery_document(document, config)
