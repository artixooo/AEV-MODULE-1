from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    session_token = Column(
        Text,
        nullable=False,
        unique=True
    )

    device_name = Column(
        String(150),
        nullable=True
    )

    device_type = Column(
        String(50),
        nullable=True
    )

    ip_address = Column(
        String(50),
        nullable=True
    )

    user_agent = Column(
        Text,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    last_activity = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )
