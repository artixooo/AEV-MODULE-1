import pytest
from unittest.mock import MagicMock, patch
from hvac.exceptions import InvalidPath, Forbidden, Unauthorized, VaultError
from app.vault.idp import (
    IdpSecretManager,
    IdpSecretNotFoundError,
    IdpSecretUnauthorizedError,
    IdpSecretError,
)


class TestIdpSecretManager:

    def setup_method(self):
        self.manager = IdpSecretManager()

    def test_get_path_valid(self):
        assert self.manager.get_path("tenant-123", "oidc") == "tenants/tenant-123/idp/oidc"
        assert self.manager.get_path("550e8400-e29b-41d4-a716-446655440000", "oauth2") == "tenants/550e8400-e29b-41d4-a716-446655440000/idp/oauth2"
        assert self.manager.get_path("tenant_alpha", "saml") == "tenants/tenant_alpha/idp/saml"

    def test_get_path_invalid_provider(self):
        with pytest.raises(ValueError, match="Unsupported identity provider type"):
            self.manager.get_path("tenant-123", "ldap")

    def test_tenant_id_length_boundaries(self):
        # 2 chars: Below minimum length (rejected)
        with pytest.raises(ValueError, match="Invalid tenant_id format"):
            self.manager.validate_tenant_id("ab")

        # 3 chars: Valid lower bound (accepted)
        assert self.manager.validate_tenant_id("abc") == "abc"

        # 64 chars: Valid upper bound (accepted)
        valid_64 = "a" * 64
        assert self.manager.validate_tenant_id(valid_64) == valid_64

        # 65 chars: Above maximum length (rejected)
        invalid_65 = "a" * 65
        with pytest.raises(ValueError, match="Invalid tenant_id format"):
            self.manager.validate_tenant_id(invalid_65)

    def test_tenant_id_whitespace_rejection(self):
        with pytest.raises(ValueError, match="leading or trailing whitespace"):
            self.manager.validate_tenant_id(" tenant-123")

        with pytest.raises(ValueError, match="leading or trailing whitespace"):
            self.manager.validate_tenant_id("tenant-123 ")

    def test_tenant_id_invalid_characters(self):
        with pytest.raises(ValueError, match="Invalid tenant_id format"):
            self.manager.validate_tenant_id("../etc/passwd")

        with pytest.raises(ValueError, match="Invalid tenant_id format"):
            self.manager.validate_tenant_id("tenant/alpha")

        with pytest.raises(ValueError, match="Invalid tenant_id format"):
            self.manager.validate_tenant_id("tenant!@#$")

        with pytest.raises(ValueError, match="Tenant ID must be a non-empty string"):
            self.manager.validate_tenant_id("")

    @patch("app.vault.idp.vault_client")
    def test_read_provider_secret_success(self, mock_vault_client):
        mock_kv = MagicMock()
        mock_kv.read_secret_version.return_value = {
            "data": {
                "data": {
                    "client_secret": "mock-secret",
                    "signing_key": "mock-key"
                }
            }
        }
        mock_vault_client.client.secrets.kv.v2 = mock_kv

        data = IdpSecretManager.read_provider_secret("tenant-alpha", "oidc")
        assert data["client_secret"] == "mock-secret"
        assert data["signing_key"] == "mock-key"

    @patch("app.vault.idp.vault_client")
    def test_read_provider_secret_empty_data(self, mock_vault_client):
        mock_kv = MagicMock()
        mock_kv.read_secret_version.return_value = {"data": {"data": {}}}
        mock_vault_client.client.secrets.kv.v2 = mock_kv

        with pytest.raises(IdpSecretNotFoundError, match="No secret data found"):
            IdpSecretManager.read_provider_secret("tenant-alpha", "oidc")

    @patch("app.vault.idp.vault_client")
    def test_read_provider_secret_not_found(self, mock_vault_client):
        mock_kv = MagicMock()
        mock_kv.read_secret_version.side_effect = InvalidPath("path not found")
        mock_vault_client.client.secrets.kv.v2 = mock_kv

        with pytest.raises(IdpSecretNotFoundError, match="Secret not found at path"):
            IdpSecretManager.read_provider_secret("tenant-alpha", "oidc")

    @patch("app.vault.idp.vault_client")
    def test_read_provider_secret_forbidden(self, mock_vault_client):
        mock_kv = MagicMock()
        mock_kv.read_secret_version.side_effect = Forbidden("permission denied")
        mock_vault_client.client.secrets.kv.v2 = mock_kv

        with pytest.raises(IdpSecretUnauthorizedError, match="Vault access denied"):
            IdpSecretManager.read_provider_secret("tenant-alpha", "oidc")

    @patch("app.vault.idp.vault_client")
    def test_read_provider_secret_unauthorized(self, mock_vault_client):
        mock_kv = MagicMock()
        mock_kv.read_secret_version.side_effect = Unauthorized("invalid token")
        mock_vault_client.client.secrets.kv.v2 = mock_kv

        with pytest.raises(IdpSecretUnauthorizedError, match="Vault access denied"):
            IdpSecretManager.read_provider_secret("tenant-alpha", "oidc")

    @patch("app.vault.idp.vault_client")
    def test_read_provider_secret_vault_error(self, mock_vault_client):
        mock_kv = MagicMock()
        mock_kv.read_secret_version.side_effect = VaultError("service unavailable")
        mock_vault_client.client.secrets.kv.v2 = mock_kv

        with pytest.raises(IdpSecretError, match="Vault operation failed"):
            IdpSecretManager.read_provider_secret("tenant-alpha", "oidc")