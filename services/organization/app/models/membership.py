import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy import Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Membership(Base):
    """SQLAlchemy model for a user's membership in an organization workspace."""

    __tablename__ = "memberships"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id = Column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
    )

    organization_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    workspace_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    membership_status = Column(
        String(30),
        default="ACTIVE",
        nullable=False,
    )

    joined_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    organization = relationship(
        "Organization",
        back_populates="memberships",
    )

    workspace = relationship(
        "Workspace",
        back_populates="memberships",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "organization_id",
            "workspace_id",
            name="uq_membership",
        ),
    )
