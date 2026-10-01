"""
Pydantic Schemas — Policy Service API (v1, RBAC scope).

Author: Utkarsh Pratham (Squad Lead) & Narayanan Varadarajan
Organization: CyArt Tech LLP | AEV Platform - Pod Alpha
"""

import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role_name: str = Field(examples=["Editor"])
    role_code: str = Field(examples=["editor"])
    description: Optional[str] = None


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    permission_name: str = Field(examples=["Edit Articles"])
    permission_code: str = Field(examples=["articles:edit"])
    resource: str = Field(examples=["articles"])
    action: str = Field(examples=["edit"])


class EvaluateRequest(BaseModel):
    """
    Request body for POST /evaluate.

    role_code is supplied explicitly by the caller — the validated JWT
    proves who is calling, but does not itself carry role information
    (no service in this system currently maps a user to a role).
    """
    role_code: str = Field(examples=["editor"])
    permission_code: str = Field(examples=["articles:edit"])


class EvaluateResponse(BaseModel):
    """Standardized authorization decision returned to the caller."""
    effect: str = Field(examples=["ALLOW"], description="'ALLOW' or 'DENY'")
    reason: str = Field(
        examples=["role_has_permission"],
        description="Machine-readable reason code: role_has_permission, role_missing_permission, role_not_found, or permission_not_found.",
    )
    allowed: bool = Field(examples=[True])