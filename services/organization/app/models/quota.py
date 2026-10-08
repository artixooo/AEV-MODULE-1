from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class TenantQuota(Base):
    __tablename__ = "tenant_quotas"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    tenant_id = Column(
        String(255),
        nullable=False,
        index=True,
    )

    quota_name = Column(
        String(100),
        nullable=False,
    )

    limit_value = Column(
        Integer,
        nullable=False,
    )

    unit = Column(
        String(50),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
