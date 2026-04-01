from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuthorizedExit(Base):
    __tablename__ = "authorized_exits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    center_id: Mapped[int] = mapped_column(ForeignKey("centers.id"), nullable=False, index=True)
    school_year_id: Mapped[int] = mapped_column(ForeignKey("school_years.id"), nullable=False, index=True)

    exit_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    authorized_by_name: Mapped[str] = mapped_column(String(150), nullable=False)
    authorized_by_role: Mapped[str] = mapped_column(String(100), nullable=False)

    released_to_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    released_to_relationship: Mapped[str | None] = mapped_column(String(100), nullable=True)

    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    recorded_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    requires_guardian_pickup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    student = relationship("Student")
    center = relationship("Center")
    school_year = relationship("SchoolYear")