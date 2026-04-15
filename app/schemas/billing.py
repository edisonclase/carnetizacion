from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BillingInvoiceCreate(BaseModel):
    center_id: int
    issue_date: date
    due_date: date
    concept: str = Field(min_length=3, max_length=255)
    card_quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    amount_paid: Decimal = Field(default=Decimal("0.00"), ge=0)
    notes: str | None = None


class BillingInvoiceResponse(BaseModel):
    id: int
    center_id: int
    invoice_number: str
    issue_date: date
    due_date: date
    concept: str
    card_quantity: int
    unit_price: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    pending_amount: Decimal
    status: str
    notes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BillingPaymentCreate(BaseModel):
    payment_date: date
    amount: Decimal = Field(gt=0)
    payment_method: str = Field(default="transfer", min_length=2, max_length=50)
    reference: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=255)
    recorded_by: str | None = Field(default=None, max_length=120)


class BillingPaymentResponse(BaseModel):
    id: int
    invoice_id: int
    payment_date: date
    amount: Decimal
    payment_method: str
    reference: str | None = None
    notes: str | None = None
    recorded_by: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)