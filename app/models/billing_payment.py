from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BillingPayment(Base):
    __tablename__ = "billing_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("billing_invoices.id"),
        nullable=False,
        index=True,
    )

    payment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    payment_method: Mapped[str] = mapped_column(String(50), nullable=False, default="transfer")
    reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recorded_by: Mapped[str | None] = mapped_column(String(120), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    invoice = relationship("BillingInvoice", back_populates="payments")