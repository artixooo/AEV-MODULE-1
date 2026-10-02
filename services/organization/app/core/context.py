from typing import Any, Optional


class TenantContext:
    """
    Tenant context extracted from authenticated JWT claims.
    """

    def __init__(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        claims: Optional[dict[str, Any]] = None,
    ):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.claims = claims or {}

    @classmethod
    def from_claims(cls, claims: dict[str, Any]) -> "TenantContext":
        """
        Create tenant context from validated JWT claims.
        """

        user_id = claims.get("sub")

        if not user_id:
            raise ValueError("JWT subject claim is required")

        tenant_id = claims.get("tenant_id")

        return cls(
            user_id=str(user_id),
            tenant_id=str(tenant_id) if tenant_id is not None else None,
            claims=claims,
        )

    def is_tenant_available(self) -> bool:
        """
        Return True when a tenant ID is available.
        """

        return self.tenant_id is not None

    @property
    def is_tenant_scoped(self) -> bool:
        """
        Return True when the request is associated with a tenant.
        """

        return self.tenant_id is not None


def build_tenant_context(claims: dict[str, Any]) -> TenantContext:
    """
    Build tenant context from validated JWT claims.
    """

    return TenantContext.from_claims(claims)