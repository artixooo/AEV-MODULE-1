import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PolicyBase(BaseModel):
    name: str = Field(..., max_length=150, examples=["allow-admin-access"])
    description: Optional[str] = None
    rules: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class PolicyCreate(PolicyBase):
    """Fields required to create a new policy."""
    pass


class PolicyUpdate(BaseModel):
    """All fields optional — used for partial updates (PATCH)."""
    name: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class PolicyResponse(PolicyBase):
    """Shape returned to clients — includes system-generated fields."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
    
