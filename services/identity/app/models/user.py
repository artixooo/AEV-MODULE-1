import uuid

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    username = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )

    # Database column is password_hash
    password_hash = Column(
        Text,
        nullable=False
    )

    first_name = Column(
        String(100),
        nullable=True
    )

    last_name = Column(
        String(100),
        nullable=True
    )

    phone = Column(
        String(20),
        nullable=True
    )

    is_email_verified = Column(
        Boolean,
        default=False
    )

    is_mfa_enabled = Column(
        Boolean,
        default=False
    )

    status = Column(
        String(20),
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )