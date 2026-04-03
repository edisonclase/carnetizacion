"""expand centers for institutional identity

Revision ID: e35c581eef8d
Revises: ebbeeec2ddba
Create Date: 2026-04-03 11:05:06.882741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e35c581eef8d'
down_revision: Union[str, Sequence[str], None] = 'ebbeeec2ddba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("centers", sa.Column("letterhead_url", sa.String(length=500), nullable=True))
    op.add_column("centers", sa.Column("primary_color", sa.String(length=20), nullable=True))
    op.add_column("centers", sa.Column("secondary_color", sa.String(length=20), nullable=True))
    op.add_column("centers", sa.Column("accent_color", sa.String(length=20), nullable=True))
    op.add_column("centers", sa.Column("text_color", sa.String(length=20), nullable=True))
    op.add_column("centers", sa.Column("background_color", sa.String(length=20), nullable=True))

    op.add_column("centers", sa.Column("philosophy", sa.Text(), nullable=True))
    op.add_column("centers", sa.Column("mission", sa.Text(), nullable=True))
    op.add_column("centers", sa.Column("vision", sa.Text(), nullable=True))
    op.add_column("centers", sa.Column("values", sa.Text(), nullable=True))

    op.add_column("centers", sa.Column("motto", sa.String(length=255), nullable=True))
    op.add_column("centers", sa.Column("address", sa.String(length=255), nullable=True))
    op.add_column("centers", sa.Column("phone", sa.String(length=100), nullable=True))
    op.add_column("centers", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("centers", sa.Column("district_name", sa.String(length=255), nullable=True))
    op.add_column("centers", sa.Column("management_code", sa.String(length=100), nullable=True))


def downgrade():
    op.drop_column("centers", "management_code")
    op.drop_column("centers", "district_name")
    op.drop_column("centers", "email")
    op.drop_column("centers", "phone")
    op.drop_column("centers", "address")
    op.drop_column("centers", "motto")

    op.drop_column("centers", "values")
    op.drop_column("centers", "vision")
    op.drop_column("centers", "mission")
    op.drop_column("centers", "philosophy")

    op.drop_column("centers", "background_color")
    op.drop_column("centers", "text_color")
    op.drop_column("centers", "accent_color")
    op.drop_column("centers", "secondary_color")
    op.drop_column("centers", "primary_color")
    op.drop_column("centers", "letterhead_url")
