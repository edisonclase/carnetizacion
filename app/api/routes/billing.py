from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.billing import (
    BillingInvoiceCreate,
    BillingInvoiceResponse,
    BillingPaymentCreate,
    BillingPaymentResponse,
)
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


def _super_admin_only():
    return require_roles(UserRole.SUPER_ADMIN)


@router.post(
    "/invoices",
    response_model=BillingInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(
    payload: BillingInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_only()),
):
    service = BillingService(db)

    try:
        return service.create_invoice(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/invoices", response_model=list[BillingInvoiceResponse])
def list_invoices(
    center_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_only()),
):
    service = BillingService(db)
    return service.list_invoices(center_id=center_id, status=status)


@router.get("/invoices/{invoice_id}", response_model=BillingInvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_only()),
):
    service = BillingService(db)

    try:
        return service.get_invoice(invoice_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/invoices/{invoice_id}/payments",
    response_model=BillingPaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_payment(
    invoice_id: int,
    payload: BillingPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_only()),
):
    service = BillingService(db)

    try:
        return service.register_payment(invoice_id=invoice_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/invoices/{invoice_id}/payments",
    response_model=list[BillingPaymentResponse],
)
def list_invoice_payments(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_only()),
):
    service = BillingService(db)

    try:
        return service.list_invoice_payments(invoice_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/payments/{payment_id}", response_model=BillingPaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_super_admin_only()),
):
    service = BillingService(db)

    try:
        return service.get_payment(payment_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc