from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

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

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "sessions.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    token_hash = Column(
        Text,
        nullable=False,
        unique=True
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    revoked = Column(
        Boolean,
        default=False
    )

    revoked_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )