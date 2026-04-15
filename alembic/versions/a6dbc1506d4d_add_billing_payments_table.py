"""add billing payments table

Revision ID: 9b6e4a8f0c21
Revises: 3763e846ccb5
Create Date: 2026-04-15 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b6e4a8f0c21"
down_revision: Union[str, Sequence[str], None] = "5f9f370964e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "billing_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.Integer(), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("payment_method", sa.String(length=50), nullable=False),
        sa.Column("reference", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("recorded_by", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["billing_invoices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_billing_payments_id"), "billing_payments", ["id"], unique=False)
    op.create_index(op.f("ix_billing_payments_invoice_id"), "billing_payments", ["invoice_id"], unique=False)
    op.create_index(op.f("ix_billing_payments_payment_date"), "billing_payments", ["payment_date"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_billing_payments_payment_date"), table_name="billing_payments")
    op.drop_index(op.f("ix_billing_payments_invoice_id"), table_name="billing_payments")
    op.drop_index(op.f("ix_billing_payments_id"), table_name="billing_payments")
    op.drop_table("billing_payments")