"""add authorized exit tolerance to center schedules

Revision ID: ebbeeec2ddba
Revises: d68b4877a0cd
Create Date: 2026-04-02 08:47:45.597186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ebbeeec2ddba"
down_revision: Union[str, Sequence[str], None] = "d68b4877a0cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "center_schedules",
        sa.Column(
            "authorized_exit_tolerance_minutes",
            sa.Integer(),
            nullable=False,
            server_default="15",
        ),
    )

    op.alter_column(
        "center_schedules",
        "authorized_exit_tolerance_minutes",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("center_schedules", "authorized_exit_tolerance_minutes")
