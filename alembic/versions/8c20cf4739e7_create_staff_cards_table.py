"""create staff cards table

Revision ID: 8c20cf4739e7
Revises: 21aec3fa888a
Create Date: 2026-04-19 05:45:46.663404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c20cf4739e7'
down_revision: Union[str, Sequence[str], None] = '21aec3fa888a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "staff_cards",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("staff_id", sa.Integer(), sa.ForeignKey("staff.id"), nullable=False),
        sa.Column("card_code", sa.String(length=50), nullable=False),
        sa.Column("qr_token", sa.String(length=255), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_staff_cards_id", "staff_cards", ["id"], unique=False)
    op.create_index("ix_staff_cards_staff_id", "staff_cards", ["staff_id"], unique=False)
    op.create_index("ix_staff_cards_card_code", "staff_cards", ["card_code"], unique=True)
    op.create_index("ix_staff_cards_qr_token", "staff_cards", ["qr_token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_staff_cards_qr_token", table_name="staff_cards")
    op.drop_index("ix_staff_cards_card_code", table_name="staff_cards")
    op.drop_index("ix_staff_cards_staff_id", table_name="staff_cards")
    op.drop_index("ix_staff_cards_id", table_name="staff_cards")
    op.drop_table("staff_cards")