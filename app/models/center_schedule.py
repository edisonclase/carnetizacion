from datetime import datetime, time

from sqlalchemy import DateTime, ForeignKey, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CenterSchedule(Base):
    __tablename__ = "center_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    center_id: Mapped[int] = mapped_column(
        ForeignKey("centers.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    entry_time: Mapped[time] = mapped_column(Time, nullable=False)
    exit_time: Mapped[time] = mapped_column(Time, nullable=False)

    workdays: Mapped[str] = mapped_column(String(50), nullable=False)

    late_tolerance_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    absence_cutoff_time: Mapped[time] = mapped_column(Time, nullable=False)
    early_dismissal_threshold_time: Mapped[time] = mapped_column(Time, nullable=False)

    minimum_attendance_for_school_day: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    early_dismissal_percentage_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=40)
    authorized_exit_tolerance_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    center = relationship("Center")