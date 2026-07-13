import uuid

from app.domain.exceptions.invoice_payment import ReceiptNotFoundException
from app.domain.repositories.invoice_payment_repository import InvoicePaymentRepository
from app.application.dtos.invoice_payment import ReceiptResponse


class ReceiptService:
    def __init__(self, invoice_payment_repository: InvoicePaymentRepository):
        self._payment_repo = invoice_payment_repository

    async def generate_receipt_json(self, payment_id: uuid.UUID) -> ReceiptResponse:
        """
        Generates a flattened JSON structure suitable for PDF printing.
        """
        payment = await self._payment_repo.get_by_id(payment_id)
        if not payment:
            raise ReceiptNotFoundException()
            
        # Ensure relations are loaded
        invoice = payment.invoice
        party = invoice.party
        trip = invoice.trip
        
        collector_name = payment.receiver.name if payment.receiver else "System"

        return ReceiptResponse(
            receipt_number=payment.receipt_number,
            invoice_number=invoice.invoice_number,
            trip_number=trip.trip_number,
            party_name=party.name,
            gst_number=party.gst_number,
            pan_number=party.pan_number,
            mobile_number=party.mobile_number,
            payment_date=payment.payment_date,
            payment_source=payment.payment_source,
            amount=payment.amount,
            balance=invoice.balance_amount,
            transaction_number=payment.transaction_number,
            cheque_number=payment.cheque_number,
            bank_name=payment.bank_name,
            collector_name=collector_name,
            remarks=payment.remarks,
        )
