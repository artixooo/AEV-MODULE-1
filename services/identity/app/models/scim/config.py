from dataclasses import dataclass


@dataclass
class SCIMConfiguration:
    """
    Tenant-scoped SCIM configuration.

    This model represents SCIM provisioning configuration and is
    intentionally separate from SCIM User and Group resource models.
    """

    tenant_id: str
    enabled: bool = True
    endpoint: str = "/scim/v2"
    provisioning_enabled: bool = True
    status: str = "active"