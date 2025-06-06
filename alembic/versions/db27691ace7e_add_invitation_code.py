"""add invitation code

Revision ID: db27691ace7e
Revises: e1d704e09e4f
Create Date: 2025-02-16 23:42:26.275142

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes

# revision identifiers, used by Alembic.
revision: str = "db27691ace7e"
down_revision: Union[str, None] = "e1d704e09e4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "invitationcode",
        sa.Column(
            "invitation_code",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("expired_at", sa.Integer(), nullable=False),
        sa.Column("redeem_limit", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.PrimaryKeyConstraint("invitation_code"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("invitationcode")
    # ### end Alembic commands ###
