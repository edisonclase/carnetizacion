from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CenterAttendanceDay(Base):
    __tablename__ = "center_attendance_days"
    __table_args__ = (
        UniqueConstraint(
            "center_id",
            "school_year_id",
            "date",
            name="uq_center_school_year_date",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    center_id: Mapped[int] = mapped_column(ForeignKey("centers.id"), nullable=False, index=True)
    school_year_id: Mapped[int] = mapped_column(ForeignKey("school_years.id"), nullable=False, index=True)

    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    is_workday: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    had_attendance_activity: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    possible_no_school_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    possible_early_dismissal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    total_entries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_exits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    total_present: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_late: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_absent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_with_excuse: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    center = relationship("Center")
    school_year = relationship("SchoolYear")