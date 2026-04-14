from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


VALID_BILLING_STATUSES = {
    "pending",
    "partial",
    "paid",
    "overdue",
    "cancelled",
}


class BillingInvoiceBase(BaseModel):
    center_id: int
    issue_date: date
    due_date: date | None = None
    concept: str = "Emisión de carnets"
    card_quantity: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0)
    notes: str | None = None

    @field_validator("concept")
    @classmethod
    def validate_concept(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El concepto es obligatorio.")
        return value


class BillingInvoiceCreate(BillingInvoiceBase):
    amount_paid: Decimal = Field(default=0, ge=0)


class BillingInvoiceUpdate(BaseModel):
    issue_date: date | None = None
    due_date: date | None = None
    concept: str | None = None
    card_quantity: int | None = Field(default=None, ge=1)
    unit_price: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None
    status: str | None = None

    @field_validator("concept")
    @classmethod
    def validate_optional_concept(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("El concepto no puede estar vacío.")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().lower()
        if value not in VALID_BILLING_STATUSES:
            raise ValueError("Estado de factura no válido.")
        return value


class BillingPaymentApply(BaseModel):
    amount: Decimal = Field(gt=0)
    notes: str | None = None


class BillingInvoiceResponse(BaseModel):
    id: int
    center_id: int
    invoice_number: str
    issue_date: date
    due_date: date | None
    concept: str
    card_quantity: int
    unit_price: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    pending_amount: Decimal
    status: str
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CenterBillingSummaryResponse(BaseModel):
    center_id: int
    total_invoices: int
    total_billed: Decimal
    total_paid: Decimal
    total_pending: Decimal
    pending_invoices: int
    partial_invoices: int
    paid_invoices: int
    overdue_invoices: int