"""add gender to staff and create staff attendance events

Revision ID: a8315ce95d5b
Revises: 8c20cf4739e7
Create Date: 2026-04-19 09:45:33.490584
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a8315ce95d5b"
down_revision: Union[str, Sequence[str], None] = "8c20cf4739e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "staff",
        sa.Column("gender", sa.String(length=20), nullable=True),
    )
    op.create_index("ix_staff_gender", "staff", ["gender"], unique=False)

    op.create_table(
        "staff_attendance_events",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("staff_id", sa.Integer(), sa.ForeignKey("staff.id"), nullable=False),
        sa.Column("staff_card_id", sa.Integer(), sa.ForeignKey("staff_cards.id"), nullable=True),
        sa.Column("center_id", sa.Integer(), sa.ForeignKey("centers.id"), nullable=False),
        sa.Column("school_year_id", sa.Integer(), sa.ForeignKey("school_years.id"), nullable=True),
        sa.Column("event_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False, server_default="scanner"),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("recorded_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_staff_attendance_events_id", "staff_attendance_events", ["id"], unique=False)
    op.create_index("ix_staff_attendance_events_staff_id", "staff_attendance_events", ["staff_id"], unique=False)
    op.create_index("ix_staff_attendance_events_staff_card_id", "staff_attendance_events", ["staff_card_id"], unique=False)
    op.create_index("ix_staff_attendance_events_center_id", "staff_attendance_events", ["center_id"], unique=False)
    op.create_index("ix_staff_attendance_events_school_year_id", "staff_attendance_events", ["school_year_id"], unique=False)
    op.create_index("ix_staff_attendance_events_event_type", "staff_attendance_events", ["event_type"], unique=False)
    op.create_index("ix_staff_attendance_events_status", "staff_attendance_events", ["status"], unique=False)
    op.create_index("ix_staff_attendance_events_event_time", "staff_attendance_events", ["event_time"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_staff_attendance_events_event_time", table_name="staff_attendance_events")
    op.drop_index("ix_staff_attendance_events_status", table_name="staff_attendance_events")
    op.drop_index("ix_staff_attendance_events_event_type", table_name="staff_attendance_events")
    op.drop_index("ix_staff_attendance_events_school_year_id", table_name="staff_attendance_events")
    op.drop_index("ix_staff_attendance_events_center_id", table_name="staff_attendance_events")
    op.drop_index("ix_staff_attendance_events_staff_card_id", table_name="staff_attendance_events")
    op.drop_index("ix_staff_attendance_events_staff_id", table_name="staff_attendance_events")
    op.drop_index("ix_staff_attendance_events_id", table_name="staff_attendance_events")
    op.drop_table("staff_attendance_events")

    op.drop_index("ix_staff_gender", table_name="staff")
    op.drop_column("staff", "gender")