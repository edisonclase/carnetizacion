from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
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

    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)

    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)

    concept: Mapped[str] = mapped_column(String(255), nullable=False)

    card_quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    pending_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    center = relationship("Center")
    payments = relationship(
        "BillingPayment",
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="BillingPayment.payment_date.desc(), BillingPayment.id.desc()",
    )