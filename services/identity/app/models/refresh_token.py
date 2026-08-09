from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class RefreshToken(Base):

    __tablename__ = "refresh_tokens"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String(255),
        nullable=False
    )

    token = Column(
        String(500),
        nullable=False,
        unique=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )