from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.billing import (
    BillingInvoiceCreate,
    BillingInvoiceResponse,
    BillingInvoiceUpdate,
    BillingPaymentApply,
    CenterBillingSummaryResponse,
)
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


def _super_admin_dependency():
    return require_roles(UserRole.SUPER_ADMIN)


@router.post(
    "/invoices",
    response_model=BillingInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_billing_invoice(
    payload: BillingInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_dependency()),
):
    service = BillingService(db)

    try:
        return service.create_invoice(
            center_id=payload.center_id,
            issue_date=payload.issue_date,
            due_date=payload.due_date,
            concept=payload.concept,
            card_quantity=payload.card_quantity,
            unit_price=payload.unit_price,
            amount_paid=payload.amount_paid,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/invoices", response_model=list[BillingInvoiceResponse])
def list_billing_invoices(
    center_id: int | None = Query(default=None),
    status_value: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_dependency()),
):
    service = BillingService(db)
    return service.list_invoices(center_id=center_id, status=status_value)


@router.get("/invoices/{invoice_id}", response_model=BillingInvoiceResponse)
def get_billing_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_dependency()),
):
    service = BillingService(db)

    try:
        return service.get_invoice(invoice_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/invoices/{invoice_id}", response_model=BillingInvoiceResponse)
def update_billing_invoice(
    invoice_id: int,
    payload: BillingInvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_dependency()),
):
    service = BillingService(db)

    try:
        return service.update_invoice(
            invoice_id=invoice_id,
            issue_date=payload.issue_date,
            due_date=payload.due_date,
            concept=payload.concept,
            card_quantity=payload.card_quantity,
            unit_price=payload.unit_price,
            notes=payload.notes,
            status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/invoices/{invoice_id}/apply-payment", response_model=BillingInvoiceResponse)
def apply_billing_payment(
    invoice_id: int,
    payload: BillingPaymentApply,
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_dependency()),
):
    service = BillingService(db)

    try:
        return service.apply_payment(
            invoice_id=invoice_id,
            amount=payload.amount,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/centers/{center_id}/summary", response_model=CenterBillingSummaryResponse)
def get_center_billing_summary(
    center_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_dependency()),
):
    service = BillingService(db)

    try:
        return service.get_center_summary(center_id=center_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc