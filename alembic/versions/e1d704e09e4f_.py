"""empty message

Revision ID: e1d704e09e4f
Revises: 
Create Date: 2025-02-15 03:02:19.441890

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "e1d704e09e4f"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("starting_date", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "projectmember",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column(
            "user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "role",
            sa.Enum("OWNER", "COLLABORATOR", name="role"),
            nullable=False,
        ),
        sa.Column("joined_at", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.PrimaryKeyConstraint("project_id", "user_id"),
    )


def downgrade() -> None:
    op.drop_table("projectmember")
    op.drop_table("project")
