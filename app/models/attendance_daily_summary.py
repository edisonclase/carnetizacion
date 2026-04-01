from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AttendanceDailySummary(Base):
    __tablename__ = "attendance_daily_summary"
    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uq_student_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)

    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    # valores esperados:
    # present
    # late
    # absent

    has_excuse: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    excuse_note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    first_entry_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    minutes_late: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    student = relationship("Student")