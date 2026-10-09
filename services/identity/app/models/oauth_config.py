from sqlalchemy import Boolean, Column, DateTime, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class OAuthConfig(Base):
    """
    OAuth provider configuration.

    client_secret_ref stores only a reference to the secret.
    The actual client secret must never be stored here.
    """

    __tablename__ = "oauth_provider_configs"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "provider",
            name="uq_oauth_provider_configs_tenant_provider",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    provider = Column(
        String(100),
        nullable=False,
        index=True,
    )

    client_id = Column(
        String(255),
        nullable=False,
    )

    client_secret_ref = Column(
        String(255),
        nullable=False,
    )

    authorization_url = Column(
        Text,
        nullable=False,
    )

    token_url = Column(
        Text,
        nullable=False,
    )

    redirect_uri = Column(
        Text,
        nullable=False,
    )

    scopes = Column(
        Text,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
    )

    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
