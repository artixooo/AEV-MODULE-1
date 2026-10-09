from dataclasses import dataclass, field
from typing import Any


@dataclass
class SCIMUser:
    """
    SCIM User domain model.

    This model represents the SCIM resource boundary and is intentionally
    separate from the existing Identity Service authentication user model.
    """

    id: str
    user_name: str
    active: bool = True
    name: dict[str, Any] = field(default_factory=dict)
    emails: list[dict[str, Any]] = field(default_factory=list)
    tenant_id: str | None = None
