import logging
import pytest
from unittest.mock import MagicMock, patch

from hvac.exceptions import Forbidden, InvalidPath, VaultError

from app.vault.tenant_secrets import (
    TenantSecretManager,
    TenantSecretNotFoundError,
    TenantSecretUnauthorizedError,
    TenantSecretError,
)


class TestTenantSecretIsolationAndSecurity:
    """Security tests verifying tenant isolation boundaries and zero-leak logging."""

    def test_tenant_a_and_tenant_b_independent_access(self):
        """Verify Tenant A and Tenant B retrieve their respective secrets independently."""
        mock_kv = MagicMock()
        mock_kv.read_secret_version.side_effect = [
            {"data": {"data": {"api_token": "token-for-tenant-a"}}},
            {"data": {"data": {"api_token": "token-for-tenant-b"}}},
        ]

        with patch("app.vault.tenant_secrets.vault_client") as mock_vault_client:
            mock_vault_client.client.secrets.kv.v2 = mock_kv

            secret_a = TenantSecretManager.read_tenant_config(
                "tenant-a",
                "integrations",
                "jira",
            )
            secret_b = TenantSecretManager.read_tenant_config(
                "tenant-b",
                "integrations",
                "jira",
            )

            assert secret_a["api_token"] == "token-for-tenant-a"
            assert secret_b["api_token"] == "token-for-tenant-b"

    def test_cross_tenant_access_denial_enforcement(self):
        """
        Verify that a client entity authenticated as Tenant A is denied access
        when attempting to read Tenant B's secrets.
        """
        authenticated_tenant = "tenant-a"
        forbidden_tenant = "tenant-b"

        def simulate_vault_acl(path, mount_point="secret"):
            expected_prefix = f"tenants/{authenticated_tenant}/"

            if not path.startswith(expected_prefix):
                raise Forbidden(
                    f"ACL denied: Token for {authenticated_tenant} cannot access {path}"
                )

            return {"data": {"data": {"db_user": "user_tenant_a"}}}

        mock_kv = MagicMock()
        mock_kv.read_secret_version.side_effect = simulate_vault_acl

        with patch("app.vault.tenant_secrets.vault_client") as mock_vault_client:
            mock_vault_client.client.secrets.kv.v2 = mock_kv

            # Accessing own tenant succeeds
            own_secret = TenantSecretManager.read_tenant_config(
                authenticated_tenant,
                "database",
                "postgres",
            )

            assert own_secret["db_user"] == "user_tenant_a"

            # Accessing another tenant's path is denied
            with pytest.raises(
                TenantSecretUnauthorizedError,
                match="Access denied reading tenant secret",
            ):
                TenantSecretManager.read_tenant_config(
                    forbidden_tenant,
                    "database",
                    "postgres",
                )

    def test_zero_leak_payload_logging(self, caplog):
        """Assert that secret payload values never appear in log records or stdout."""
        sensitive_password = "SUPER_CONFIDENTIAL_DB_PASSWORD_XYZ"

        with patch("app.vault.tenant_secrets.vault_client") as mock_vault_client:
            mock_vault_client.client.secrets.kv.v2.create_or_update_secret = (
                MagicMock()
            )

            with caplog.at_level(logging.INFO, logger="secrets-service"):
                TenantSecretManager.write_tenant_config(
                    "tenant-a",
                    "database",
                    "postgres",
                    {"db_pass": sensitive_password},
                )

        # Confirm plaintext secret is not in logs,
        # but safe metadata is recorded.
        assert sensitive_password not in caplog.text
        assert caplog.records[-1].tenant_id == "tenant-a"
        assert caplog.records[-1].category == "database"

    def test_unauthorized_token_leak_prevention(self, caplog):
        """Assert Vault tokens in exception messages are not leaked to log records."""
        leaked_token = "hvs.CAESIB_SECRET_VAULT_TOKEN_12345"

        mock_kv = MagicMock()
        mock_kv.read_secret_version.side_effect = Forbidden(
            f"permission denied with token {leaked_token}"
        )

        with patch("app.vault.tenant_secrets.vault_client") as mock_vault_client:
            mock_vault_client.client.secrets.kv.v2 = mock_kv

            with caplog.at_level(logging.ERROR, logger="secrets-service"):
                with pytest.raises(TenantSecretUnauthorizedError):
                    TenantSecretManager.read_tenant_config(
                        "tenant-a",
                        "database",
                        "postgres",
                    )

        assert leaked_token not in caplog.text


class TestTenantSecretManagerValidation:

    def test_get_config_path_valid(self):
        path = TenantSecretManager.get_config_path(
            "tenant-alpha",
            "database",
            "postgres",
        )

        assert path == "tenants/tenant-alpha/config/database/postgres"

    def test_get_service_path_valid(self):
        path = TenantSecretManager.get_service_path(
            "tenant-alpha",
            "asset-scanner",
        )

        assert path == "tenants/tenant-alpha/services/asset-scanner"

    @pytest.mark.parametrize(
        "tenant_id, category, key",
        [
            ("ab", "database", "postgres"),
            ("a" * 65, "database", "postgres"),
            ("tenant-alpha", "", "postgres"),
            ("tenant-alpha", "database", ""),
            ("tenant/traversal", "database", "postgres"),
            ("tenant-alpha", "../config", "key"),
            ("tenant-alpha", "database", "key/invalid"),
            ("tenant$special", "database", "postgres"),
        ],
    )
    def test_path_boundary_and_traversal_rejection(
        self,
        tenant_id,
        category,
        key,
    ):
        with pytest.raises(ValueError):
            TenantSecretManager.get_config_path(
                tenant_id,
                category,
                key,
            )

    @pytest.mark.parametrize(
        "tenant_id",
        [
            " tenant-alpha",
            "tenant-alpha ",
            " tenant-alpha ",
        ],
    )
    def test_whitespace_rejection(self, tenant_id):
        with pytest.raises(
            ValueError,
            match="leading or trailing whitespace",
        ):
            TenantSecretManager.get_config_path(
                tenant_id,
                "database",
                "postgres",
            )

    def test_read_tenant_secret_empty_payload_raises_not_found(self):
        mock_kv = MagicMock()

        mock_kv.read_secret_version.return_value = {
            "data": {
                "data": {}
            }
        }

        with patch(
            "app.vault.tenant_secrets.vault_client"
        ) as mock_vault:
            mock_vault.client.secrets.kv.v2 = mock_kv

            with pytest.raises(
                TenantSecretNotFoundError,
                match="empty or not found",
            ):
                TenantSecretManager.read_tenant_config(
                    "tenant-alpha",
                    "db",
                    "empty_key",
                )

    def test_read_tenant_secret_not_found_raises_typed_error(self):
        mock_kv = MagicMock()

        mock_kv.read_secret_version.side_effect = InvalidPath(
            "path not found"
        )

        with patch(
            "app.vault.tenant_secrets.vault_client"
        ) as mock_vault:
            mock_vault.client.secrets.kv.v2 = mock_kv

            with pytest.raises(TenantSecretNotFoundError):
                TenantSecretManager.read_tenant_config(
                    "tenant-alpha",
                    "db",
                    "missing_key",
                )