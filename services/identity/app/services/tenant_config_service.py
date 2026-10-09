from dataclasses import dataclass
from uuid import UUID


DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = 7
DEFAULT_SESSION_EXPIRE_DAYS = 7
DEFAULT_MFA_ENABLED = False


@dataclass(frozen=True)
class TenantAuthConfig:
    tenant_id: UUID
    access_token_expire_minutes: int = DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_expire_days: int = DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS
    session_expire_days: int = DEFAULT_SESSION_EXPIRE_DAYS
    mfa_enabled: bool = DEFAULT_MFA_ENABLED

    def __post_init__(self):
        if not isinstance(self.tenant_id, UUID):
            raise ValueError("tenant_id must be a valid UUID")

        if self.access_token_expire_minutes <= 0:
            raise ValueError("access_token_expire_minutes must be greater than 0")

        if self.refresh_token_expire_days <= 0:
            raise ValueError("refresh_token_expire_days must be greater than 0")

        if self.session_expire_days <= 0:
            raise ValueError("session_expire_days must be greater than 0")


class TenantConfigurationProvider:
    """
    Boundary for tenant configuration supplied by Configuration Service.

    The provider receives an authenticated tenant_id directly. It must not
    infer or substitute an organization_id.
    """

    def get_auth_config(self, tenant_id: UUID) -> TenantAuthConfig:
        raise NotImplementedError


class DefaultTenantConfigurationProvider(TenantConfigurationProvider):
    """
    Temporary safe-default provider.

    Configuration Service integration is intentionally kept behind the
    provider boundary until its tenant-aware HTTP contract is available.
    """

    def get_auth_config(self, tenant_id: UUID) -> TenantAuthConfig:
        return TenantAuthConfig(tenant_id=tenant_id)
