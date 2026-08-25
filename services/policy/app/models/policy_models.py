from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Boolean, Text, Integer, ForeignKey, DateTime, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import JSONB
from app.core.guid import GUID

# Native JSONB on Postgres (matches the migration schema exactly);
# falls back to plain JSON on other backends (e.g. SQLite in tests).
JSONType = JSON().with_variant(JSONB(), "postgresql")
from sqlalchemy.orm import relationship
from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    role_name = Column(String(100), nullable=False)
    role_code = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)
    status = Column(String(30), default="ACTIVE")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    permission_name = Column(String(150), nullable=False)
    permission_code = Column(String(100), nullable=False, unique=True)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    role_id = Column(GUID(), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(GUID(), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )


class Policy(Base):
    __tablename__ = "policies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    policy_name = Column(String(150), nullable=False)
    policy_code = Column(String(100), nullable=False, unique=True)
    resource = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)
    effect = Column(String(10), nullable=False, default="ALLOW")
    conditions = Column(JSONType, nullable=False, default=dict)
    priority = Column(Integer, default=100)
    is_system = Column(Boolean, default=True)
    status = Column(String(30), default="ACTIVE")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class SoDPolicy(Base):
    __tablename__ = "sod_policies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(150), nullable=False, unique=True)
    conflicting_roles = Column(JSONType, nullable=False, default=list)
    conflicting_permissions = Column(JSONType, nullable=False, default=list)
    description = Column(Text, nullable=True)
    severity = Column(String(30), default="HIGH")
    status = Column(String(30), default="ACTIVE")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
