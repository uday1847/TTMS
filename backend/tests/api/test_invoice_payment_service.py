import uuid
from decimal import Decimal
import pytest
from unittest.mock import AsyncMock

from app.application.services.invoice_payment_service import InvoicePaymentService
from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_payment import InvoicePayment
from app.domain.enums.invoice_status import InvoiceStatus
from app.domain.enums.payment_status import PaymentStatus
from app.domain.exceptions.invoice_payment import InvoicePaymentExceededException

@pytest.fixture
def mock_payment_repo():
    repo = AsyncMock()
    return repo

@pytest.fixture
def mock_invoice_repo():
    repo = AsyncMock()
    return repo

@pytest.fixture
def service(mock_payment_repo, mock_invoice_repo):
    return InvoicePaymentService(mock_payment_repo, mock_invoice_repo)

@pytest.mark.asyncio
async def test_recalculate_invoice_totals_success(service, mock_invoice_repo):
    invoice = Invoice(
        id=uuid.uuid4(),
        gross_amount=Decimal("10000.00"),
        received_amount=Decimal("0.00"),
        balance_amount=Decimal("10000.00"),
        status=InvoiceStatus.ISSUED,
        payments=[]
    )
    
    # 1. Partial payment
    payment1 = InvoicePayment(
        amount=Decimal("4000.00"),
        payment_status=PaymentStatus.SUCCESS,
        deleted_at=None
    )
    invoice.payments.append(payment1)
    
    await service._recalculate_invoice_totals(invoice, uuid.uuid4())
    
    assert invoice.received_amount == Decimal("4000.00")
    assert invoice.balance_amount == Decimal("6000.00")
    assert invoice.status == InvoiceStatus.PARTIALLY_PAID
    
    # 2. Full payment
    payment2 = InvoicePayment(
        amount=Decimal("6000.00"),
        payment_status=PaymentStatus.SUCCESS,
        deleted_at=None
    )
    invoice.payments.append(payment2)
    
    await service._recalculate_invoice_totals(invoice, uuid.uuid4())
    
    assert invoice.received_amount == Decimal("10000.00")
    assert invoice.balance_amount == Decimal("0.00")
    assert invoice.status == InvoiceStatus.PAID
    
    # Verify save was called
    assert mock_invoice_repo.save.call_count == 2

@pytest.mark.asyncio
async def test_recalculate_invoice_totals_exceeded(service):
    invoice = Invoice(
        id=uuid.uuid4(),
        gross_amount=Decimal("10000.00"),
        received_amount=Decimal("0.00"),
        balance_amount=Decimal("10000.00"),
        status=InvoiceStatus.ISSUED,
        payments=[]
    )
    
    payment = InvoicePayment(
        amount=Decimal("12000.00"),
        payment_status=PaymentStatus.SUCCESS,
        deleted_at=None
    )
    invoice.payments.append(payment)
    
    with pytest.raises(InvoicePaymentExceededException):
        await service._recalculate_invoice_totals(invoice, uuid.uuid4())
