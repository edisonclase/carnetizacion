"""create staff table

Revision ID: 21aec3fa888a
Revises: add_center_card_config_fields
Create Date: 2026-04-18 19:34:30.020506

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21aec3fa888a'
down_revision: Union[str, Sequence[str], None] = 'add_center_card_config_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "staff",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("center_id", sa.Integer(), sa.ForeignKey("centers.id"), nullable=False),
        sa.Column("school_year_id", sa.Integer(), sa.ForeignKey("school_years.id"), nullable=True),

        sa.Column("first_name", sa.String(length=150), nullable=False),
        sa.Column("last_name", sa.String(length=150), nullable=False),
        sa.Column("staff_code", sa.String(length=50), nullable=False),
        sa.Column("national_id", sa.String(length=50), nullable=True),
        sa.Column("photo_path", sa.String(length=500), nullable=True),

        sa.Column("staff_group", sa.String(length=50), nullable=False),
        sa.Column("staff_position", sa.String(length=100), nullable=False),
        sa.Column("department", sa.String(length=150), nullable=True),

        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_staff_id", "staff", ["id"], unique=False)
    op.create_index("ix_staff_center_id", "staff", ["center_id"], unique=False)
    op.create_index("ix_staff_school_year_id", "staff", ["school_year_id"], unique=False)
    op.create_index("ix_staff_staff_code", "staff", ["staff_code"], unique=False)
    op.create_index("ix_staff_staff_group", "staff", ["staff_group"], unique=False)
    op.create_index("ix_staff_staff_position", "staff", ["staff_position"], unique=False)

    op.create_unique_constraint(
        "uq_staff_center_id_staff_code",
        "staff",
        ["center_id", "staff_code"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_staff_center_id_staff_code", "staff", type_="unique")
    op.drop_index("ix_staff_staff_position", table_name="staff")
    op.drop_index("ix_staff_staff_group", table_name="staff")
    op.drop_index("ix_staff_staff_code", table_name="staff")
    op.drop_index("ix_staff_school_year_id", table_name="staff")
    op.drop_index("ix_staff_center_id", table_name="staff")
    op.drop_index("ix_staff_id", table_name="staff")
    op.drop_table("staff")

