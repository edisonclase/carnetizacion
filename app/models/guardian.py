from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Guardian(Base):
    __tablename__ = "guardians"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False)

    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)

    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    student = relationship("Student")