from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    center_id: Mapped[int] = mapped_column(
        ForeignKey("centers.id"),
        nullable=False,
        index=True,
    )

    school_year_id: Mapped[int | None] = mapped_column(
        ForeignKey("school_years.id"),
        nullable=True,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    staff_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    national_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    gender: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)

    staff_group: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    staff_position: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    department: Mapped[str | None] = mapped_column(String(150), nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    center = relationship("Center", backref="staff_members")
    school_year = relationship("SchoolYear", backref="staff_members")