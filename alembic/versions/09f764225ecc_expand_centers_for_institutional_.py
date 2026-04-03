"""expand centers for institutional identity

Revision ID: 09f764225ecc
Revises: e35c581eef8d
Create Date: 2026-04-03 11:10:53.024311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09f764225ecc'
down_revision: Union[str, Sequence[str], None] = 'e35c581eef8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
