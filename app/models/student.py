from datetime import date

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint(
            "center_id",
            "school_year_id",
            "student_code",
            name="uq_student_center_year_code",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    center_id: Mapped[int] = mapped_column(ForeignKey("centers.id"), nullable=False, index=True)
    school_year_id: Mapped[int] = mapped_column(ForeignKey("school_years.id"), nullable=False, index=True)

    # 🔹 Código interno del sistema (TUYO)
    student_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # 🔹 ID oficial MINERD (opcional)
    minerd_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)

    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)

    grade: Mapped[str] = mapped_column(String(50), nullable=False)
    section: Mapped[str] = mapped_column(String(50), nullable=False)

    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    center = relationship("Center")
    school_year = relationship("SchoolYear")