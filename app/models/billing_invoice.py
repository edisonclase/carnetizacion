from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BillingInvoice(Base):
    __tablename__ = "billing_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    center_id: Mapped[int] = mapped_column(
        ForeignKey("centers.id"),
        nullable=False,
        index=True,
    )

    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    issue_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    concept: Mapped[str] = mapped_column(String(150), nullable=False, default="Emisión de carnets")
    card_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    pending_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    center = relationship("Center")