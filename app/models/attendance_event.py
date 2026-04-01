from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AttendanceEvent(Base):
    __tablename__ = "attendance_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    card_id: Mapped[int | None] = mapped_column(ForeignKey("cards.id"), nullable=True, index=True)

    event_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    status: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)

    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(String(30), nullable=False, default="scanner")
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recorded_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    student = relationship("Student")
    card = relationship("Card")