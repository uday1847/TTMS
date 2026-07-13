from datetime import date, datetime
from decimal import Decimal
import uuid
from typing import Sequence, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_status_history import InvoiceStatusHistory
from app.domain.enums.invoice_status import InvoiceStatus
from app.domain.repositories.invoice_repository import InvoiceRepository
from app.domain.repositories.trip_repository import TripRepository
from app.domain.exceptions.trip import TripNotFoundException
from app.domain.exceptions.invoice import (
    InvoiceNotFoundException,
    InvoiceAlreadyExistsException,
    InvoiceStatusException,
    InvoicePaymentException,
    InvoiceGenerationException,
)
from app.application.dtos.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceStatusUpdate,
)
from app.application.services.invoice_number_generator import InvoiceNumberGenerator


class InvoiceService:
    """
    Orchestrates business processes and validations for generating and managing Invoices.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: InvoiceRepository,
        trip_repository: TripRepository,
        generator: InvoiceNumberGenerator,
    ) -> None:
        self.session = session
        self.repository = repository
        self.trip_repository = trip_repository
        self.generator = generator

    async def create_invoice(self, dto: InvoiceCreate, user_id: uuid.UUID) -> Invoice:
        """
        Validates a completed trip and customer, calculates billing amounts,
        generates sequential invoice numbers, and creates the draft invoice.
        """
        trip = await self.trip_repository.get_by_id(dto.trip_id)
        if not trip:
            raise TripNotFoundException(dto.trip_id)

        # 1. Validation pre-checks
        if trip.deleted_at is not None or not trip.is_active:
            raise InvoiceGenerationException("Cannot generate invoices for soft-deleted or inactive trips.")

        if trip.status.value != "COMPLETED":
            raise InvoiceGenerationException(f"Invoices can only be generated for COMPLETED trips. Current trip status is {trip.status.value}.")

        if trip.freight_amount <= Decimal("0.00"):
            raise InvoiceGenerationException("Trip freight amount must be greater than zero to generate an invoice.")

        # Check existing active invoice
        existing = await self.repository.get_by_trip(dto.trip_id)
        if existing and existing.status != InvoiceStatus.CANCELLED:
            raise InvoiceAlreadyExistsException(dto.trip_id)

        # Check active Party
        if not trip.party or not trip.party.is_active or trip.party.deleted_at is not None:
            raise InvoiceGenerationException("Associated customer party is inactive or deleted.")

        # Validate delivery date bounds
        delivery_date = trip.actual_delivery_date or trip.trip_date
        if dto.invoice_date < delivery_date:
            raise InvoiceGenerationException(f"Invoice date {dto.invoice_date} cannot be earlier than trip delivery/start date {delivery_date}.")

        # Generate invoice number
        invoice_number = await self.generator.generate()

        # Compute financial amounts
        gross_amount = trip.freight_amount
        received_amount = Decimal("0.00")
        balance_amount = gross_amount - received_amount

        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number=invoice_number,
            trip_id=dto.trip_id,
            party_id=trip.party_id,
            invoice_date=dto.invoice_date,
            due_date=dto.due_date,
            gross_amount=gross_amount,
            received_amount=received_amount,
            balance_amount=balance_amount,
            remarks=dto.remarks,
            status=InvoiceStatus.DRAFT,
            created_by=user_id,
            updated_by=user_id,
            is_active=True,
        )

        await self.repository.create(invoice)

        # Log audit history trail
        history = InvoiceStatusHistory(
            id=uuid.uuid4(),
            invoice_id=invoice.id,
            old_status=None,
            new_status=InvoiceStatus.DRAFT.value,
            remarks="Invoice generated and saved in DRAFT state.",
            changed_by=user_id,
        )
        self.session.add(history)

        await self.session.commit()
        return await self.repository.get_by_id(invoice.id)

    async def update_invoice(self, invoice_id: uuid.UUID, dto: InvoiceUpdate, user_id: uuid.UUID) -> Invoice:
        """
        Updates basic invoice details. Enforces state-based editing restrictions.
        """
        invoice = await self.repository.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException(invoice_id)

        # Enforce read-only final states
        if invoice.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
            raise InvoiceStatusException(f"Invoices in {invoice.status.value} status are read-only and cannot be modified.")

        # Partially paid edits check
        if invoice.status == InvoiceStatus.PARTIALLY_PAID:
            if dto.invoice_date is not None or dto.due_date is not None:
                raise InvoiceStatusException("Cannot update dates or amounts on a partially paid invoice.")

        # Update allowed values
        if dto.remarks is not None:
            invoice.remarks = dto.remarks

        if invoice.status in (InvoiceStatus.DRAFT, InvoiceStatus.ISSUED):
            new_invoice_date = dto.invoice_date if dto.invoice_date is not None else invoice.invoice_date
            new_due_date = dto.due_date if dto.due_date is not None else invoice.due_date

            if new_due_date < new_invoice_date:
                raise InvoiceStatusException("due_date must be greater than or equal to invoice_date.")

            if dto.invoice_date is not None:
                # Re-validate trip delivery boundary
                trip = await self.trip_repository.get_by_id(invoice.trip_id)
                if trip:
                    delivery_date = trip.actual_delivery_date or trip.trip_date
                    if dto.invoice_date < delivery_date:
                        raise InvoiceStatusException(f"Invoice date cannot be earlier than trip delivery date {delivery_date}.")
                invoice.invoice_date = dto.invoice_date

            if dto.due_date is not None:
                invoice.due_date = dto.due_date

        invoice.updated_by = user_id
        invoice.updated_at = datetime.now()

        await self.repository.update(invoice)
        await self.session.commit()
        return await self.repository.get_by_id(invoice.id)

    async def update_status(self, invoice_id: uuid.UUID, dto: InvoiceStatusUpdate, user_id: uuid.UUID) -> Invoice:
        """
        Orchestrates status workflow state transitions and logs historical audits.
        """
        invoice = await self.repository.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException(invoice_id)

        old_status = invoice.status
        new_status = dto.status

        if old_status == new_status:
            return invoice

        # State transition matrix rules validation
        if old_status == InvoiceStatus.DRAFT:
            if new_status not in (InvoiceStatus.ISSUED, InvoiceStatus.CANCELLED):
                raise InvoiceStatusException(f"Invalid transition from DRAFT to {new_status.value}. Allowed transitions: ISSUED, CANCELLED.")
        elif old_status == InvoiceStatus.ISSUED:
            if new_status not in (InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID):
                raise InvoiceStatusException(f"Invalid transition from ISSUED to {new_status.value}. Allowed transitions: PARTIALLY_PAID, PAID.")
        elif old_status == InvoiceStatus.PARTIALLY_PAID:
            if new_status != InvoiceStatus.PAID:
                raise InvoiceStatusException(f"Invalid transition from PARTIALLY_PAID to {new_status.value}. Allowed transitions: PAID.")
        elif old_status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
            raise InvoiceStatusException(f"Cannot transition status from final state: {old_status.value}.")

        # Log audit entry
        history = InvoiceStatusHistory(
            id=uuid.uuid4(),
            invoice_id=invoice.id,
            old_status=old_status.value,
            new_status=new_status.value,
            remarks=dto.remarks or f"Invoice status changed from {old_status.value} to {new_status.value}.",
            changed_by=user_id,
        )
        self.session.add(history)

        invoice.status = new_status
        invoice.updated_by = user_id
        invoice.updated_at = datetime.now()

        await self.repository.update(invoice)
        await self.session.commit()
        return await self.repository.get_by_id(invoice.id)

    async def record_payment(self, invoice_id: uuid.UUID, amount: Decimal, remarks: str | None, user_id: uuid.UUID) -> Invoice:
        """
        Derives received amount updates. Automatically transitions status to PARTIALLY_PAID or PAID.
        """
        invoice = await self.repository.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException(invoice_id)

        if amount <= Decimal("0.00"):
            raise InvoicePaymentException("Payment amount must be greater than zero.")

        if invoice.status in (InvoiceStatus.DRAFT, InvoiceStatus.CANCELLED):
            raise InvoicePaymentException("Payments can only be recorded on ISSUED or PARTIALLY_PAID invoices.")

        if invoice.status == InvoiceStatus.PAID:
            raise InvoicePaymentException("Invoice is already fully PAID.")

        old_status = invoice.status
        new_received = invoice.received_amount + amount

        if new_received > invoice.gross_amount:
            raise InvoicePaymentException(f"Payment amount of {amount} exceeds outstanding balance of {invoice.balance_amount}.")

        invoice.received_amount = new_received
        invoice.balance_amount = invoice.gross_amount - new_received

        new_status = InvoiceStatus.PAID if invoice.balance_amount == Decimal("0.00") else InvoiceStatus.PARTIALLY_PAID

        # Log state transition if changed
        if old_status != new_status:
            history = InvoiceStatusHistory(
                id=uuid.uuid4(),
                invoice_id=invoice.id,
                old_status=old_status.value,
                new_status=new_status.value,
                remarks=remarks or f"Payment of {amount} recorded. Balance outstanding is {invoice.balance_amount}.",
                changed_by=user_id,
            )
            self.session.add(history)
            invoice.status = new_status

        invoice.updated_by = user_id
        invoice.updated_at = datetime.now()

        await self.repository.update(invoice)
        await self.session.commit()
        return await self.repository.get_by_id(invoice.id)

    async def delete_invoice(self, invoice_id: uuid.UUID, user_id: uuid.UUID) -> Invoice:
        """
        Soft deletes an invoice. Enforces that only DRAFT invoices are deletable.
        """
        invoice = await self.repository.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException(invoice_id)

        if invoice.status != InvoiceStatus.DRAFT:
            raise InvoiceStatusException("Only invoices in DRAFT status can be deleted to preserve financial audits.")

        invoice.deleted_at = datetime.now()
        invoice.is_active = False
        invoice.updated_by = user_id

        await self.repository.update(invoice)
        await self.session.commit()
        await self.session.refresh(invoice)
        return invoice

    async def get_invoice_by_id(self, invoice_id: uuid.UUID) -> Invoice:
        """
        Retrieves a single invoice by ID.
        """
        invoice = await self.repository.get_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundException(invoice_id)
        return invoice
