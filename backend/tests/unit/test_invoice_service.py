import datetime
from decimal import Decimal
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services.invoice_service import InvoiceService
from app.application.services.invoice_number_generator import InvoiceNumberGenerator
from app.domain.entities.invoice import Invoice
from app.domain.entities.invoice_status_history import InvoiceStatusHistory
from app.domain.entities.trip import Trip
from app.domain.entities.party import Party
from app.domain.enums.invoice_status import InvoiceStatus
from app.domain.enums.trip_status import TripStatus
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


@pytest.fixture
def mock_repo() -> MagicMock:
    repo = MagicMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_trip = AsyncMock()
    repo.get_invoice_dashboard_summary = AsyncMock()
    repo.get_invoice_status_history = AsyncMock()
    return repo


@pytest.fixture
def mock_trip_repo() -> MagicMock:
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_generator() -> MagicMock:
    generator = MagicMock(spec=InvoiceNumberGenerator)
    generator.generate = AsyncMock(return_value="INV-2026-000001")
    return generator


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def service(
    mock_session: MagicMock,
    mock_repo: MagicMock,
    mock_trip_repo: MagicMock,
    mock_generator: MagicMock,
) -> InvoiceService:
    return InvoiceService(mock_session, mock_repo, mock_trip_repo, mock_generator)


@pytest.mark.asyncio
async def test_create_invoice_success(
    service: InvoiceService,
    mock_repo: MagicMock,
    mock_trip_repo: MagicMock,
    mock_generator: MagicMock,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    party_id = uuid.uuid4()
    user_id = uuid.uuid4()

    party = Party(id=party_id, name="IOCL", is_active=True)
    trip = Trip(
        id=trip_id,
        trip_number="TRIP-001",
        status=TripStatus.COMPLETED,
        freight_amount=Decimal("45000.00"),
        advance_amount=Decimal("10000.00"),
        party_id=party_id,
        party=party,
        actual_delivery_date=datetime.date.today() - datetime.timedelta(days=2),
        is_active=True,
    )
    mock_trip_repo.get_by_id.return_value = trip
    mock_repo.get_by_trip.return_value = None

    dto = InvoiceCreate(
        trip_id=trip_id,
        invoice_date=datetime.date.today(),
        due_date=datetime.date.today() + datetime.timedelta(days=15),
        remarks="Test invoice",
    )

    mock_repo.create.side_effect = lambda x: x
    mock_repo.get_by_id.side_effect = lambda x: mock_repo.create.call_args[0][0]

    # Act
    invoice = await service.create_invoice(dto, user_id)

    # Assert
    assert invoice.invoice_number == "INV-2026-000001"
    assert invoice.gross_amount == Decimal("45000.00")
    assert invoice.balance_amount == Decimal("45000.00")
    assert invoice.status == InvoiceStatus.DRAFT
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_invoice_trip_not_completed(
    service: InvoiceService,
    mock_trip_repo: MagicMock,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    trip = Trip(id=trip_id, status=TripStatus.DISPATCHED, is_active=True)
    mock_trip_repo.get_by_id.return_value = trip

    dto = InvoiceCreate(
        trip_id=trip_id,
        invoice_date=datetime.date.today(),
        due_date=datetime.date.today() + datetime.timedelta(days=15),
    )

    # Act & Assert
    with pytest.raises(InvoiceGenerationException) as exc:
        await service.create_invoice(dto, uuid.uuid4())
    assert "Invoices can only be generated for COMPLETED trips" in str(exc.value)


@pytest.mark.asyncio
async def test_create_invoice_duplicate_trip(
    service: InvoiceService,
    mock_repo: MagicMock,
    mock_trip_repo: MagicMock,
) -> None:
    # Arrange
    trip_id = uuid.uuid4()
    party = Party(id=uuid.uuid4(), name="IOCL", is_active=True)
    trip = Trip(
        id=trip_id,
        status=TripStatus.COMPLETED,
        freight_amount=Decimal("100.00"),
        party=party,
        is_active=True,
    )
    mock_trip_repo.get_by_id.return_value = trip
    mock_repo.get_by_trip.return_value = Invoice(id=uuid.uuid4(), status=InvoiceStatus.ISSUED)

    dto = InvoiceCreate(
        trip_id=trip_id,
        invoice_date=datetime.date.today(),
        due_date=datetime.date.today() + datetime.timedelta(days=10),
    )

    # Act & Assert
    with pytest.raises(InvoiceAlreadyExistsException):
        await service.create_invoice(dto, uuid.uuid4())


@pytest.mark.asyncio
async def test_update_invoice_partially_paid_restrictions(
    service: InvoiceService,
    mock_repo: MagicMock,
) -> None:
    # Arrange
    invoice_id = uuid.uuid4()
    invoice = Invoice(
        id=invoice_id,
        invoice_number="INV-001",
        status=InvoiceStatus.PARTIALLY_PAID,
        gross_amount=Decimal("100.00"),
        received_amount=Decimal("40.00"),
        balance_amount=Decimal("60.00"),
    )
    mock_repo.get_by_id.return_value = invoice

    dto = InvoiceUpdate(invoice_date=datetime.date.today())

    # Act & Assert
    with pytest.raises(InvoiceStatusException) as exc:
        await service.update_invoice(invoice_id, dto, uuid.uuid4())
    assert "Cannot update dates or amounts on a partially paid invoice" in str(exc.value)


@pytest.mark.asyncio
async def test_status_transitions_workflow(
    service: InvoiceService,
    mock_repo: MagicMock,
) -> None:
    # Arrange
    invoice_id = uuid.uuid4()
    invoice = Invoice(id=invoice_id, status=InvoiceStatus.DRAFT)
    mock_repo.get_by_id.return_value = invoice
    mock_repo.update.side_effect = lambda x: x

    # 1. Draft to Issued (Success)
    dto = InvoiceStatusUpdate(status=InvoiceStatus.ISSUED, remarks="Mailed to customer")
    updated = await service.update_status(invoice_id, dto, uuid.uuid4())
    assert updated.status == InvoiceStatus.ISSUED

    # 2. Issued to Draft (Invalid transition)
    invoice.status = InvoiceStatus.ISSUED
    dto_invalid = InvoiceStatusUpdate(status=InvoiceStatus.DRAFT)
    with pytest.raises(InvoiceStatusException):
        await service.update_status(invoice_id, dto_invalid, uuid.uuid4())


@pytest.mark.asyncio
async def test_record_payment_derived_workflow(
    service: InvoiceService,
    mock_repo: MagicMock,
) -> None:
    # Arrange
    invoice_id = uuid.uuid4()
    invoice = Invoice(
        id=invoice_id,
        status=InvoiceStatus.ISSUED,
        gross_amount=Decimal("500.00"),
        received_amount=Decimal("0.00"),
        balance_amount=Decimal("500.00"),
    )
    mock_repo.get_by_id.return_value = invoice
    mock_repo.update.side_effect = lambda x: x

    # 1. Recording partial payment
    updated = await service.record_payment(invoice_id, Decimal("200.00"), "Received cheque", uuid.uuid4())
    assert updated.received_amount == Decimal("200.00")
    assert updated.balance_amount == Decimal("300.00")
    assert updated.status == InvoiceStatus.PARTIALLY_PAID

    # 2. Recording settlement payment
    invoice.status = InvoiceStatus.PARTIALLY_PAID
    updated_final = await service.record_payment(invoice_id, Decimal("300.00"), "Balance cash payment", uuid.uuid4())
    assert updated_final.received_amount == Decimal("500.00")
    assert updated_final.balance_amount == Decimal("0.00")
    assert updated_final.status == InvoiceStatus.PAID


@pytest.mark.asyncio
async def test_soft_delete_restrictions(
    service: InvoiceService,
    mock_repo: MagicMock,
) -> None:
    # Arrange
    invoice_id = uuid.uuid4()
    invoice = Invoice(id=invoice_id, status=InvoiceStatus.ISSUED)
    mock_repo.get_by_id.return_value = invoice

    # Act & Assert
    with pytest.raises(InvoiceStatusException) as exc:
        await service.delete_invoice(invoice_id, uuid.uuid4())
    assert "Only invoices in DRAFT status can be deleted" in str(exc.value)
