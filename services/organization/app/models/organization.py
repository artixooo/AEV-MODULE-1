from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class Organization(Base):
    """SQLAlchemy model for the Organization entity."""

    __tablename__ = "organizations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    organization_name = Column(
        String(255),
        nullable=False,
    )

    organization_code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    website = Column(
        String(255),
        nullable=True,
    )

    status = Column(
        String(30),
        default="ACTIVE",
        nullable=False,
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