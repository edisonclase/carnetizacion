from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.billing_invoice import BillingInvoice
from app.models.center import Center


TWOPLACES = Decimal("0.01")


class BillingService:
    def __init__(self, db: Session):
        self.db = db

    def _round_money(self, value: Decimal | int | float) -> Decimal:
        return Decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def _get_center_or_404(self, center_id: int) -> Center:
        center = self.db.query(Center).filter(Center.id == center_id).first()
        if not center:
            raise ValueError("Centro no encontrado.")
        return center

    def _build_invoice_number(self, center_id: int) -> str:
        count = (
            self.db.query(BillingInvoice)
            .filter(BillingInvoice.center_id == center_id)
            .count()
        )
        return f"FAC-{center_id:03d}-{count + 1:05d}"

    def _resolve_status(
        self,
        *,
        total_amount: Decimal,
        amount_paid: Decimal,
        due_date: date | None,
    ) -> str:
        if amount_paid <= Decimal("0.00"):
            if due_date and due_date < date.today():
                return "overdue"
            return "pending"

        if amount_paid >= total_amount:
            return "paid"

        if due_date and due_date < date.today():
            return "overdue"

        return "partial"

    def create_invoice(
        self,
        *,
        center_id: int,
        issue_date: date,
        due_date: date | None,
        concept: str,
        card_quantity: int,
        unit_price: Decimal,
        amount_paid: Decimal,
        notes: str | None,
    ) -> BillingInvoice:
        self._get_center_or_404(center_id)

        unit_price = self._round_money(unit_price)
        amount_paid = self._round_money(amount_paid)

        total_amount = self._round_money(Decimal(card_quantity) * unit_price)
        pending_amount = self._round_money(total_amount - amount_paid)

        if amount_paid > total_amount:
            raise ValueError("El monto pagado no puede ser mayor que el monto total.")

        status = self._resolve_status(
            total_amount=total_amount,
            amount_paid=amount_paid,
            due_date=due_date,
        )

        invoice = BillingInvoice(
            center_id=center_id,
            invoice_number=self._build_invoice_number(center_id),
            issue_date=issue_date,
            due_date=due_date,
            concept=concept,
            card_quantity=card_quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            amount_paid=amount_paid,
            pending_amount=pending_amount,
            status=status,
            notes=notes,
        )

        self.db.add(invoice)
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
            query = query.filter(BillingInvoice.status == status.strip().lower())

        return query.order_by(BillingInvoice.id.desc()).all()

    def get_invoice(self, invoice_id: int) -> BillingInvoice:
        invoice = (
            self.db.query(BillingInvoice)
            .filter(BillingInvoice.id == invoice_id)
            .first()
        )
        if not invoice:
            raise ValueError("Factura no encontrada.")
        return invoice

    def update_invoice(
        self,
        *,
        invoice_id: int,
        issue_date: date | None,
        due_date: date | None,
        concept: str | None,
        card_quantity: int | None,
        unit_price: Decimal | None,
        notes: str | None,
        status: str | None,
    ) -> BillingInvoice:
        invoice = self.get_invoice(invoice_id)

        if issue_date is not None:
            invoice.issue_date = issue_date

        if due_date is not None:
            invoice.due_date = due_date

        if concept is not None:
            invoice.concept = concept

        if card_quantity is not None:
            invoice.card_quantity = card_quantity

        if unit_price is not None:
            invoice.unit_price = self._round_money(unit_price)

        if notes is not None:
            invoice.notes = notes

        invoice.total_amount = self._round_money(
            Decimal(invoice.card_quantity) * Decimal(invoice.unit_price)
        )

        if invoice.amount_paid > invoice.total_amount:
            raise ValueError("El monto pagado actual supera el nuevo total de la factura.")

        invoice.pending_amount = self._round_money(invoice.total_amount - invoice.amount_paid)

        if status is not None:
            invoice.status = status
        else:
            invoice.status = self._resolve_status(
                total_amount=Decimal(invoice.total_amount),
                amount_paid=Decimal(invoice.amount_paid),
                due_date=invoice.due_date,
            )

        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def apply_payment(
        self,
        *,
        invoice_id: int,
        amount: Decimal,
        notes: str | None,
    ) -> BillingInvoice:
        invoice = self.get_invoice(invoice_id)

        amount = self._round_money(amount)

        new_amount_paid = self._round_money(Decimal(invoice.amount_paid) + amount)
        if new_amount_paid > Decimal(invoice.total_amount):
            raise ValueError("El pago excede el monto total de la factura.")

        invoice.amount_paid = new_amount_paid
        invoice.pending_amount = self._round_money(
            Decimal(invoice.total_amount) - Decimal(invoice.amount_paid)
        )
        invoice.status = self._resolve_status(
            total_amount=Decimal(invoice.total_amount),
            amount_paid=Decimal(invoice.amount_paid),
            due_date=invoice.due_date,
        )

        if notes:
            base_notes = invoice.notes.strip() if invoice.notes else ""
            payment_note = f"Pago aplicado: {amount}"
            invoice.notes = f"{base_notes}\n{payment_note}\n{notes}".strip()
        else:
            base_notes = invoice.notes.strip() if invoice.notes else ""
            payment_note = f"Pago aplicado: {amount}"
            invoice.notes = f"{base_notes}\n{payment_note}".strip()

        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_center_summary(self, *, center_id: int) -> dict:
        self._get_center_or_404(center_id)

        invoices = (
            self.db.query(BillingInvoice)
            .filter(BillingInvoice.center_id == center_id)
            .all()
        )

        total_billed = self._round_money(sum(Decimal(item.total_amount) for item in invoices) if invoices else 0)
        total_paid = self._round_money(sum(Decimal(item.amount_paid) for item in invoices) if invoices else 0)
        total_pending = self._round_money(sum(Decimal(item.pending_amount) for item in invoices) if invoices else 0)

        return {
            "center_id": center_id,
            "total_invoices": len(invoices),
            "total_billed": total_billed,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "pending_invoices": sum(1 for item in invoices if item.status == "pending"),
            "partial_invoices": sum(1 for item in invoices if item.status == "partial"),
            "paid_invoices": sum(1 for item in invoices if item.status == "paid"),
            "overdue_invoices": sum(1 for item in invoices if item.status == "overdue"),
        }