"""add center card config fields

Revision ID: add_center_card_config_fields
Revises: 9b6e4a8f0c21
Create Date: 2026-04-18
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_center_card_config_fields"
down_revision = '9b6e4a8f0c21'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("centers", sa.Column("card_loss_notice", sa.String(length=255), nullable=True))
    op.add_column("centers", sa.Column("card_loss_contact", sa.String(length=255), nullable=True))
    op.add_column("centers", sa.Column("card_show_technical_area", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.add_column("centers", sa.Column("card_technical_area_label", sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column("centers", "card_technical_area_label")
    op.drop_column("centers", "card_show_technical_area")
    op.drop_column("centers", "card_loss_contact")
    op.drop_column("centers", "card_loss_notice")