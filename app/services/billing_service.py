from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.billing_invoice import BillingInvoice
from app.models.billing_payment import BillingPayment
from app.models.center import Center
from app.schemas.billing import BillingInvoiceCreate, BillingPaymentCreate


TWO_PLACES = Decimal("0.01")


def _to_money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


class BillingService:
    def __init__(self, db: Session):
        self.db = db

    def _get_center_or_raise(self, center_id: int) -> Center:
        center = self.db.query(Center).filter(Center.id == center_id).first()
        if not center:
            raise ValueError("El centro indicado no existe.")
        return center

    def _get_invoice_or_raise(self, invoice_id: int) -> BillingInvoice:
        invoice = self.db.query(BillingInvoice).filter(BillingInvoice.id == invoice_id).first()
        if not invoice:
            raise ValueError("La factura no existe.")
        return invoice

    def _build_invoice_number(self, center_id: int) -> str:
        count = (
            self.db.query(BillingInvoice)
            .filter(BillingInvoice.center_id == center_id)
            .count()
        )
        next_number = count + 1
        return f"FAC-{center_id:03d}-{next_number:05d}"

    def _recalculate_invoice_totals(self, invoice: BillingInvoice) -> None:
        payments = (
            self.db.query(BillingPayment)
            .filter(BillingPayment.invoice_id == invoice.id)
            .all()
        )

        total_paid = sum((_to_money(payment.amount) for payment in payments), Decimal("0.00"))
        total_amount = _to_money(invoice.total_amount)
        pending_amount = total_amount - total_paid

        if pending_amount < Decimal("0.00"):
            raise ValueError("Los pagos superan el total de la factura.")

        invoice.amount_paid = _to_money(total_paid)
        invoice.pending_amount = _to_money(pending_amount)

        if invoice.amount_paid == Decimal("0.00"):
            invoice.status = "pending"
        elif invoice.pending_amount == Decimal("0.00"):
            invoice.status = "paid"
        else:
            invoice.status = "partial"

    def create_invoice(self, payload: BillingInvoiceCreate) -> BillingInvoice:
        self._get_center_or_raise(payload.center_id)

        if payload.due_date < payload.issue_date:
            raise ValueError("La fecha de vencimiento no puede ser menor que la fecha de emisión.")

        quantity = int(payload.card_quantity)
        unit_price = _to_money(payload.unit_price)
        upfront_paid = _to_money(payload.amount_paid)

        total_amount = _to_money(Decimal(quantity) * unit_price)

        if upfront_paid > total_amount:
            raise ValueError("El monto pagado no puede ser mayor que el total de la factura.")

        invoice = BillingInvoice(
            center_id=payload.center_id,
            invoice_number=self._build_invoice_number(payload.center_id),
            issue_date=payload.issue_date,
            due_date=payload.due_date,
            concept=payload.concept.strip(),
            card_quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            amount_paid=Decimal("0.00"),
            pending_amount=total_amount,
            status="pending",
            notes=payload.notes.strip() if payload.notes else None,
        )

        self.db.add(invoice)
        self.db.flush()

        if upfront_paid > Decimal("0.00"):
            opening_payment = BillingPayment(
                invoice_id=invoice.id,
                payment_date=payload.issue_date,
                amount=upfront_paid,
                payment_method="initial",
                reference=None,
                notes="Pago inicial registrado al crear la factura.",
                recorded_by="system",
            )
            self.db.add(opening_payment)
            self.db.flush()

        self._recalculate_invoice_totals(invoice)

        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def list_invoices(
        self,
        *,
        center_id: int | None = None,
        status: str | None = None,
    ) -> list[BillingInvoice]:
        query = self.db.query(BillingInvoice)

        if center_id is not None:
            query = query.filter(BillingInvoice.center_id == center_id)

        if status:
            query = query.filter(BillingInvoice.status == status)

        return query.order_by(BillingInvoice.id.desc()).all()

    def get_invoice(self, invoice_id: int) -> BillingInvoice:
        return self._get_invoice_or_raise(invoice_id)

    def register_payment(
        self,
        *,
        invoice_id: int,
        payload: BillingPaymentCreate,
    ) -> BillingPayment:
        invoice = self._get_invoice_or_raise(invoice_id)

        payment_amount = _to_money(payload.amount)
        current_pending = _to_money(invoice.pending_amount)

        if payment_amount <= Decimal("0.00"):
            raise ValueError("El monto del pago debe ser mayor que cero.")

        if invoice.status == "paid":
            raise ValueError("La factura ya está saldada.")

        if payment_amount > current_pending:
            raise ValueError("El monto del pago no puede superar el balance pendiente.")

        payment = BillingPayment(
            invoice_id=invoice.id,
            payment_date=payload.payment_date,
            amount=payment_amount,
            payment_method=payload.payment_method.strip(),
            reference=payload.reference.strip() if payload.reference else None,
            notes=payload.notes.strip() if payload.notes else None,
            recorded_by=payload.recorded_by.strip() if payload.recorded_by else None,
        )

        self.db.add(payment)
        self.db.flush()

        self._recalculate_invoice_totals(invoice)

        self.db.commit()
        self.db.refresh(payment)

        return payment

    def list_invoice_payments(self, invoice_id: int) -> list[BillingPayment]:
        self._get_invoice_or_raise(invoice_id)

        return (
            self.db.query(BillingPayment)
            .filter(BillingPayment.invoice_id == invoice_id)
            .order_by(BillingPayment.payment_date.desc(), BillingPayment.id.desc())
            .all()
        )

    def get_payment(self, payment_id: int) -> BillingPayment:
        payment = self.db.query(BillingPayment).filter(BillingPayment.id == payment_id).first()
        if not payment:
            raise ValueError("El pago no existe.")
        return payment