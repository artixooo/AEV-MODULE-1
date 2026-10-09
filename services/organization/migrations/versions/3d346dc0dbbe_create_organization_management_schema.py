"""create organization management schema

Revision ID: 3d346dc0dbbe
Revises:
Create Date: 2026-09-11 17:40:27.308745

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "3d346dc0dbbe"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply Organization Service schema changes."""

    # ---------------------------------------------------------
    # Organizations
    # ---------------------------------------------------------

    op.add_column(
        "organizations",
        sa.Column(
            "parent_organization_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_organizations_parent_organization_id",
        "organizations",
        ["parent_organization_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_parent_organization",
        "organizations",
        "organizations",
        ["parent_organization_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ---------------------------------------------------------
    # Organization existing columns
    # ---------------------------------------------------------

    op.alter_column(
        "organizations",
        "status",
        existing_type=sa.VARCHAR(length=30),
        nullable=False,
        existing_server_default=sa.text("'ACTIVE'::character varying"),
    )

    op.alter_column(
        "organizations",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "organizations",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    # ---------------------------------------------------------
    # Memberships
    # ---------------------------------------------------------

    op.alter_column(
        "memberships",
        "membership_status",
        existing_type=sa.VARCHAR(length=30),
        nullable=False,
        existing_server_default=sa.text("'ACTIVE'::character varying"),
    )

    op.alter_column(
        "memberships",
        "joined_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "memberships",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.create_index(
        "ix_memberships_id",
        "memberships",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_memberships_user_id",
        "memberships",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_memberships_organization_id",
        "memberships",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_memberships_workspace_id",
        "memberships",
        ["workspace_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # Workspaces
    # ---------------------------------------------------------

    op.alter_column(
        "workspaces",
        "status",
        existing_type=sa.VARCHAR(length=30),
        nullable=False,
        existing_server_default=sa.text("'ACTIVE'::character varying"),
    )

    op.alter_column(
        "workspaces",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "workspaces",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.create_index(
        "ix_workspaces_id",
        "workspaces",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_workspaces_organization_id",
        "workspaces",
        ["organization_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # Projects
    # ---------------------------------------------------------

    op.alter_column(
        "projects",
        "status",
        existing_type=sa.VARCHAR(length=30),
        nullable=False,
        existing_server_default=sa.text("'PLANNING'::character varying"),
    )

    op.alter_column(
        "projects",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "projects",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.create_index(
        "ix_projects_id",
        "projects",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_projects_workspace_id",
        "projects",
        ["workspace_id"],
        unique=False,
    )


def downgrade() -> None:
    """Revert Organization Service schema changes."""

    # ---------------------------------------------------------
    # Projects
    # ---------------------------------------------------------

    op.drop_index(
        "ix_projects_workspace_id",
        table_name="projects",
    )

    op.drop_index(
        "ix_projects_id",
        table_name="projects",
    )

    op.alter_column(
        "projects",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "projects",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "projects",
        "status",
        existing_type=sa.VARCHAR(length=30),
        nullable=True,
        existing_server_default=sa.text("'PLANNING'::character varying"),
    )

    # ---------------------------------------------------------
    # Workspaces
    # ---------------------------------------------------------

    op.drop_index(
        "ix_workspaces_organization_id",
        table_name="workspaces",
    )

    op.drop_index(
        "ix_workspaces_id",
        table_name="workspaces",
    )

    op.alter_column(
        "workspaces",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "workspaces",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "workspaces",
        "status",
        existing_type=sa.VARCHAR(length=30),
        nullable=True,
        existing_server_default=sa.text("'ACTIVE'::character varying"),
    )

    # ---------------------------------------------------------
    # Memberships
    # ---------------------------------------------------------

    op.drop_index(
        "ix_memberships_workspace_id",
        table_name="memberships",
    )

    op.drop_index(
        "ix_memberships_organization_id",
        table_name="memberships",
    )

    op.drop_index(
        "ix_memberships_user_id",
        table_name="memberships",
    )

    op.drop_index(
        "ix_memberships_id",
        table_name="memberships",
    )

    op.alter_column(
        "memberships",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "memberships",
        "joined_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "memberships",
        "membership_status",
        existing_type=sa.VARCHAR(length=30),
        nullable=True,
        existing_server_default=sa.text("'ACTIVE'::character varying"),
    )

    # ---------------------------------------------------------
    # Organizations
    # ---------------------------------------------------------

    op.drop_constraint(
        "fk_parent_organization",
        "organizations",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_organizations_parent_organization_id",
        table_name="organizations",
    )

    op.alter_column(
        "organizations",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "organizations",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_server_default=sa.text("CURRENT_TIMESTAMP"),
    )

    op.alter_column(
        "organizations",
        "status",
        existing_type=sa.VARCHAR(length=30),
        nullable=True,
        existing_server_default=sa.text("'ACTIVE'::character varying"),
    )

    op.drop_column(
        "organizations",
        "parent_organization_id",
    )