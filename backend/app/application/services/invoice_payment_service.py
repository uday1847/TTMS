import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Tuple, Any

from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_payment import InvoicePayment
from app.domain.entities.invoice_payment_history import InvoicePaymentHistory
from app.domain.enums.invoice_status import InvoiceStatus
from app.domain.enums.payment_status import PaymentStatus
from app.domain.exceptions.invoice import InvoiceNotFoundException
from app.domain.exceptions.invoice_payment import (
    InvoicePaymentNotFoundException,
    InvoicePaymentExceededException,
    InvoiceDraftException,
    InvoiceCancelledException,
    InvoiceAlreadyPaidException,
    InvoicePaymentValidationException
)
from app.domain.repositories.invoice_payment_repository import InvoicePaymentRepository
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.application.dtos.invoice_payment import InvoicePaymentCreate, InvoicePaymentUpdate
from app.application.services.receipt_number_generator import ReceiptNumberGenerator


class InvoicePaymentService:
    def __init__(
        self,
        invoice_payment_repository: InvoicePaymentRepository,
        invoice_repository: InvoiceRepository,
    ):
        self._payment_repo = invoice_payment_repository
        self._invoice_repo = invoice_repository

    async def _recalculate_invoice_totals(self, invoice: Invoice, current_user_id: uuid.UUID) -> None:
        """
        Recalculates the invoice's received_amount, balance_amount, and status based on all active payments.
        Must be called after adding, removing, or restoring a payment.
        """
        active_payments = [p for p in invoice.payments if p.deleted_at is None and p.payment_status == PaymentStatus.SUCCESS]
        
        total_received = sum((p.amount for p in active_payments), Decimal("0.00"))
        
        if total_received > invoice.gross_amount:
            # Safely cap or raise. We prevent it on creation, but for safety:
            raise InvoicePaymentExceededException()
            
        invoice.received_amount = total_received
        invoice.balance_amount = invoice.gross_amount - total_received
        
        old_status = invoice.status
        
        if invoice.balance_amount == Decimal("0.00"):
            invoice.status = InvoiceStatus.PAID
        elif invoice.received_amount > Decimal("0.00"):
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        else:
            invoice.status = InvoiceStatus.ISSUED
            
        # Add to invoice status history if status changed
        if old_status != invoice.status:
            from app.domain.entities.invoice_status_history import InvoiceStatusHistory
            history = InvoiceStatusHistory(
                invoice_id=invoice.id,
                old_status=old_status,
                new_status=invoice.status,
                changed_by=current_user_id,
                remarks="Status updated automatically by payment processing",
            )
            invoice.status_history.append(history)
            
        await self._invoice_repo.save(invoice)

    async def create_payment(self, data: InvoicePaymentCreate, current_user_id: uuid.UUID) -> InvoicePayment:
        invoice = await self._invoice_repo.get_by_id(data.invoice_id)
        if not invoice:
            raise InvoiceNotFoundException()

        if invoice.status == InvoiceStatus.DRAFT:
            raise InvoiceDraftException()
        if invoice.status == InvoiceStatus.CANCELLED:
            raise InvoiceCancelledException()
        if invoice.status == InvoiceStatus.PAID:
            raise InvoiceAlreadyPaidException()
            
        if data.amount > invoice.balance_amount:
            raise InvoicePaymentExceededException(f"Payment amount ({data.amount}) exceeds invoice balance ({invoice.balance_amount})")

        receipt_number = await ReceiptNumberGenerator.generate()
        
        payment = InvoicePayment(
            receipt_number=receipt_number,
            invoice_id=data.invoice_id,
            payment_date=data.payment_date,
            amount=data.amount,
            payment_source=data.payment_source,
            payment_status=data.payment_status,
            bank_name=data.bank_name,
            account_holder=data.account_holder,
            transaction_number=data.transaction_number,
            cheque_number=data.cheque_number,
            cheque_date=data.cheque_date,
            reference_number=data.reference_number,
            remarks=data.remarks,
            received_by=current_user_id,
            created_by=current_user_id,
            updated_by=current_user_id,
        )
        
        history = InvoicePaymentHistory(
            payment=payment,
            old_amount=None,
            new_amount=payment.amount,
            old_status=None,
            new_status=payment.payment_status,
            old_payment_source=None,
            new_payment_source=payment.payment_source,
            remarks="Payment created",
            changed_by=current_user_id,
        )
        payment.histories = [history]
        
        # Add payment to invoice
        invoice.payments.append(payment)
        
        await self._payment_repo.save(payment)
        await self._recalculate_invoice_totals(invoice, current_user_id)
        
        return payment

    async def get_payment(self, payment_id: uuid.UUID) -> InvoicePayment:
        payment = await self._payment_repo.get_by_id(payment_id)
        if not payment:
            raise InvoicePaymentNotFoundException()
        return payment

    async def list_payments(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        invoice_id: uuid.UUID | None = None,
        party_id: uuid.UUID | None = None,
        payment_status: str | None = None,
        payment_source: str | None = None,
        sort_by: str | None = None,
        sort_desc: bool = True,
    ) -> Tuple[list[InvoicePayment], int]:
        return await self._payment_repo.get_invoice_payments(
            skip=skip,
            limit=limit,
            search=search,
            invoice_id=invoice_id,
            party_id=party_id,
            payment_status=payment_status,
            payment_source=payment_source,
            sort_by=sort_by,
            sort_desc=sort_desc
        )

    async def update_payment(self, payment_id: uuid.UUID, data: InvoicePaymentUpdate, current_user_id: uuid.UUID) -> InvoicePayment:
        payment = await self._payment_repo.get_by_id(payment_id)
        if not payment:
            raise InvoicePaymentNotFoundException()
            
        if payment.payment_status in [PaymentStatus.CANCELLED, PaymentStatus.FAILED]:
            raise InvoicePaymentValidationException("Cannot update a failed or cancelled payment")

        if data.remarks is not None:
            payment.remarks = data.remarks
            
        payment.updated_by = current_user_id
        await self._payment_repo.save(payment)
        return payment

    async def delete_payment(self, payment_id: uuid.UUID, current_user_id: uuid.UUID) -> None:
        payment = await self._payment_repo.get_by_id(payment_id)
        if not payment:
            raise InvoicePaymentNotFoundException()
            
        invoice = payment.invoice
        if invoice.status == InvoiceStatus.CANCELLED:
            raise InvoiceCancelledException("Cannot delete payment on a cancelled invoice")

        await self._payment_repo.delete(payment_id)
        
        history = InvoicePaymentHistory(
            payment_id=payment.id,
            old_amount=payment.amount,
            new_amount=payment.amount,
            old_status=payment.payment_status,
            new_status="DELETED",
            old_payment_source=payment.payment_source,
            new_payment_source=payment.payment_source,
            remarks="Payment deleted",
            changed_by=current_user_id,
        )
        await self._payment_repo._session.add(history)
        
        # Reload invoice to refresh payments relationship before recalculating
        await self._payment_repo._session.refresh(invoice)
        await self._recalculate_invoice_totals(invoice, current_user_id)

    async def restore_payment(self, payment_id: uuid.UUID, current_user_id: uuid.UUID) -> InvoicePayment:
        payment = await self._payment_repo.get_with_deleted(payment_id)
        if not payment:
            raise InvoicePaymentNotFoundException()
            
        if payment.deleted_at is None:
            return payment
            
        invoice = await self._invoice_repo.get_by_id(payment.invoice_id)
        if not invoice:
            raise InvoiceNotFoundException()
            
        if invoice.status in [InvoiceStatus.CANCELLED, InvoiceStatus.DRAFT]:
            raise InvoicePaymentValidationException("Cannot restore payment for draft or cancelled invoice")
            
        if payment.amount > invoice.balance_amount:
            raise InvoicePaymentExceededException("Restoring this payment would exceed the invoice balance")

        await self._payment_repo.restore(payment_id)
        
        history = InvoicePaymentHistory(
            payment_id=payment.id,
            old_amount=payment.amount,
            new_amount=payment.amount,
            old_status="DELETED",
            new_status=payment.payment_status,
            old_payment_source=payment.payment_source,
            new_payment_source=payment.payment_source,
            remarks="Payment restored",
            changed_by=current_user_id,
        )
        await self._payment_repo._session.add(history)
        
        await self._payment_repo._session.refresh(invoice)
        await self._recalculate_invoice_totals(invoice, current_user_id)
        
        return payment

    async def get_dashboard_metrics(self) -> dict[str, Any]:
        return await self._payment_repo.get_dashboard_metrics()
        
    async def get_payment_source_breakdown(self) -> dict[str, Any]:
        return await self._payment_repo.get_payment_source_breakdown()
