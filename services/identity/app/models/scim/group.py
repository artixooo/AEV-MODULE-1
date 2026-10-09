from dataclasses import dataclass, field
from typing import Any


@dataclass
class SCIMGroup:
    """
    SCIM Group domain model.
    """

    id: str
    display_name: str
    members: list[dict[str, Any]] = field(default_factory=list)
    tenant_id: str | None = None
