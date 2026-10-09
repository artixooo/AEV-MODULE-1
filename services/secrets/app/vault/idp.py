import re
import logging
from typing import Dict, Any
from hvac.exceptions import InvalidPath, Forbidden, Unauthorized, VaultError
from app.vault.client import vault_client

logger = logging.getLogger("secrets-service")

IDP_PATH_TEMPLATE = "tenants/{tenant_id}/idp/{provider_type}"
# Strict tenant regex: 3 to 64 alphanumeric characters, hyphens, or underscores
TENANT_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{3,64}$")
SUPPORTED_PROVIDERS = {"oauth2", "oidc", "saml"}


class IdpSecretError(Exception):
    """Base exception for IdP secret operations."""
    pass


class IdpSecretNotFoundError(IdpSecretError):
    """Raised when the requested IdP secret does not exist (404) or contains empty data."""
    pass


class IdpSecretUnauthorizedError(IdpSecretError):
    """Raised when Vault rejects authentication or authorization (401/403)."""
    pass


class IdpSecretManager:
    """
    Manages tenant-aware secret paths and retrieval for external Identity Providers.
    """

    @staticmethod
    def validate_tenant_id(tenant_id: str) -> str:
        if not tenant_id or not isinstance(tenant_id, str):
            raise ValueError("Tenant ID must be a non-empty string.")

        # Reject leading or trailing whitespace explicitly
        if tenant_id != tenant_id.strip():
            raise ValueError("Tenant ID cannot contain leading or trailing whitespace.")

        if not TENANT_ID_REGEX.match(tenant_id):
            raise ValueError(
                f"Invalid tenant_id format: '{tenant_id}'. "
                "Tenant ID must be between 3 and 64 characters (alphanumeric, hyphens, underscores only)."
            )
        return tenant_id

    @staticmethod
    def get_path(tenant_id: str, provider_type: str) -> str:
        """Constructs and validates a normalized tenant-isolated Vault secret path."""
        valid_tenant = IdpSecretManager.validate_tenant_id(tenant_id)

        if not provider_type or not isinstance(provider_type, str):
            raise ValueError("Provider type must be a non-empty string.")

        if provider_type != provider_type.strip():
            raise ValueError("Provider type cannot contain leading or trailing whitespace.")

        provider = provider_type.lower()
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported identity provider type: '{provider_type}'. Supported: {sorted(SUPPORTED_PROVIDERS)}"
            )

        return IDP_PATH_TEMPLATE.format(tenant_id=valid_tenant, provider_type=provider)

    @staticmethod
    def read_provider_secret(tenant_id: str, provider_type: str) -> Dict[str, Any]:
        """
        Retrieves tenant-specific IdP credentials from Vault KV v2 engine.

        Raises:
            IdpSecretNotFoundError: If secret is not found or empty.
            IdpSecretUnauthorizedError: If access is denied (401/403).
            IdpSecretError: For unexpected Vault or operational errors.
            ValueError: If tenant_id or provider_type fail validation.
        """
        path = IdpSecretManager.get_path(tenant_id, provider_type)
        try:
            response = vault_client.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point="secret"
            )
            data = response.get("data", {}).get("data", {})
            if not data:
                logger.warning(f"IdP secret data at {path} is empty.")
                raise IdpSecretNotFoundError(f"No secret data found at {path}")
            return data

        except InvalidPath as exc:
            logger.warning(f"IdP secret not found at path '{path}': {exc}")
            raise IdpSecretNotFoundError(f"Secret not found at path '{path}'") from exc

        except (Forbidden, Unauthorized) as exc:
            logger.error(f"Vault authorization failed for path '{path}': {exc}")
            raise IdpSecretUnauthorizedError(f"Vault access denied for path '{path}'") from exc

        except VaultError as exc:
            logger.error(f"Vault service error while reading '{path}': {exc}")
            raise IdpSecretError(f"Vault operation failed for path '{path}': {exc}") from exc

        except Exception as exc:
            if isinstance(exc, (IdpSecretNotFoundError, IdpSecretUnauthorizedError, IdpSecretError)):
                raise
            logger.error(f"Unexpected error retrieving IdP secret for '{tenant_id}/{provider_type}': {exc}")
            raise IdpSecretError(f"Unexpected error: {exc}") from exc


idp_secret_manager = IdpSecretManager()