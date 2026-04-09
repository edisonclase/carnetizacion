from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole:
    SUPER_ADMIN = "super_admin"
    ADMIN_CENTRO = "admin_centro"
    REGISTRO = "registro"
    CONSULTA = "consulta"

    ALL = {
        SUPER_ADMIN,
        ADMIN_CENTRO,
        REGISTRO,
        CONSULTA,
    }


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    center_id: Mapped[int | None] = mapped_column(
        ForeignKey("centers.id"),
        nullable=True,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    center = relationship("Center")