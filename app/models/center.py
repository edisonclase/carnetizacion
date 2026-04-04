from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Center(Base):
    __tablename__ = "centers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Identidad visual
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    letterhead_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    primary_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    secondary_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    accent_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    text_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    background_color: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Identidad institucional general
    philosophy: Mapped[str | None] = mapped_column(Text, nullable=True)
    mission: Mapped[str | None] = mapped_column(Text, nullable=True)
    vision: Mapped[str | None] = mapped_column(Text, nullable=True)
    values: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Versión corta específica para carnet
    card_philosophy: Mapped[str | None] = mapped_column(String(255), nullable=True)
    card_mission: Mapped[str | None] = mapped_column(String(255), nullable=True)
    card_vision: Mapped[str | None] = mapped_column(String(255), nullable=True)
    card_values: Mapped[str | None] = mapped_column(String(255), nullable=True)
    card_footer_text: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Datos institucionales
    motto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    district_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    management_code: Mapped[str | None] = mapped_column(String(100), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    school_years = relationship("SchoolYear", back_populates="center")