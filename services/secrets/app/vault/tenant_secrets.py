import logging
import re
from typing import Any, Dict, Optional

from hvac.exceptions import Forbidden, InvalidPath, Unauthorized, VaultError

from app.vault.client import vault_client


logger = logging.getLogger("secrets-service")

TENANT_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{3,64}$")
SECRET_KEY_REGEX = re.compile(r"^[a-zA-Z0-9_.-]{2,64}$")

TENANT_CONFIG_PATH_TEMPLATE = "tenants/{tenant_id}/config/{category}/{key}"
TENANT_SERVICE_PATH_TEMPLATE = "tenants/{tenant_id}/services/{service_name}"


class TenantSecretError(Exception):
    """Base exception for tenant-scoped secret operations."""
    pass


class TenantSecretNotFoundError(TenantSecretError):
    """Raised when the requested tenant secret path does not exist."""
    pass


class TenantSecretUnauthorizedError(TenantSecretError):
    """Raised when access is denied or cross-tenant traversal is blocked."""
    pass


class TenantSecretManager:
    """Manages tenant-partitioned secrets and enforces strict identifier boundaries."""

    @staticmethod
    def validate_identifier(
        name: str,
        value: str,
        pattern: re.Pattern,
    ) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{name} must be a string")

        if value != value.strip():
            raise ValueError(
                f"{name} must not contain leading or trailing whitespace"
            )

        if not pattern.match(value):
            raise ValueError(
                f"Invalid {name} format: '{value}'. "
                f"Must match {pattern.pattern}"
            )

        return value

    @classmethod
    def get_config_path(
        cls,
        tenant_id: str,
        category: str,
        key: str,
    ) -> str:
        cls.validate_identifier("tenant_id", tenant_id, TENANT_ID_REGEX)
        cls.validate_identifier("category", category, SECRET_KEY_REGEX)
        cls.validate_identifier("key", key, SECRET_KEY_REGEX)

        return TENANT_CONFIG_PATH_TEMPLATE.format(
            tenant_id=tenant_id,
            category=category,
            key=key,
        )

    @classmethod
    def get_service_path(
        cls,
        tenant_id: str,
        service_name: str,
    ) -> str:
        cls.validate_identifier("tenant_id", tenant_id, TENANT_ID_REGEX)
        cls.validate_identifier(
            "service_name",
            service_name,
            SECRET_KEY_REGEX,
        )

        return TENANT_SERVICE_PATH_TEMPLATE.format(
            tenant_id=tenant_id,
            service_name=service_name,
        )

    @classmethod
    def write_tenant_config(
        cls,
        tenant_id: str,
        category: str,
        key: str,
        secret_payload: Dict[str, Any],
        mount_point: str = "secret",
    ) -> None:
        path = cls.get_config_path(tenant_id, category, key)

        if not secret_payload or not isinstance(secret_payload, dict):
            raise ValueError("Secret payload must be a non-empty dictionary")

        try:
            vault_client.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secret_payload,
                mount_point=mount_point,
            )

            logger.info(
                "Tenant config secret stored successfully",
                extra={
                    "tenant_id": tenant_id,
                    "category": category,
                    "path": path,
                },
            )

        except (Forbidden, Unauthorized) as err:
            logger.error(
                "Access denied writing tenant config",
                extra={
                    "tenant_id": tenant_id,
                    "path": path,
                },
            )
            raise TenantSecretUnauthorizedError(
                f"Access denied writing tenant secret: {path}"
            ) from err

        except VaultError as err:
            logger.error(
                "Vault error writing tenant config",
                extra={
                    "tenant_id": tenant_id,
                    "path": path,
                },
            )
            raise TenantSecretError(
                f"Vault error occurred while writing tenant config: {path}"
            ) from err

    @classmethod
    def read_tenant_config(
        cls,
        tenant_id: str,
        category: str,
        key: str,
        mount_point: str = "secret",
    ) -> Dict[str, Any]:
        path = cls.get_config_path(tenant_id, category, key)

        try:
            response = vault_client.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=mount_point,
            )

            data = response.get("data", {}).get("data", {})

            if not data:
                raise TenantSecretNotFoundError(
                    f"Tenant config secret empty or not found: {path}"
                )

            logger.info(
                "Tenant config secret retrieved successfully",
                extra={
                    "tenant_id": tenant_id,
                    "category": category,
                    "path": path,
                },
            )

            return data

        except InvalidPath as err:
            logger.warning(
                "Tenant secret not found",
                extra={
                    "tenant_id": tenant_id,
                    "path": path,
                },
            )
            raise TenantSecretNotFoundError(
                f"Tenant config secret not found: {path}"
            ) from err

        except (Forbidden, Unauthorized) as err:
            logger.error(
                "Unauthorized access to tenant secret",
                extra={
                    "tenant_id": tenant_id,
                    "path": path,
                },
            )
            raise TenantSecretUnauthorizedError(
                f"Access denied reading tenant secret: {path}"
            ) from err

        except VaultError as err:
            logger.error(
                "Vault error reading tenant secret",
                extra={
                    "tenant_id": tenant_id,
                    "path": path,
                },
            )
            raise TenantSecretError(
                f"Vault error reading tenant secret: {path}"
            ) from err