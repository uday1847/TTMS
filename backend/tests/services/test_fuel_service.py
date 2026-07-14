import pytest
import uuid
from decimal import Decimal
from datetime import date, datetime
from unittest.mock import AsyncMock, patch, MagicMock

from app.domain.entities.fuel_transaction import FuelTransaction
from app.domain.entities.fuel_vendor import FuelVendor
from app.domain.entities.tractor import Tractor
from app.domain.enums.fuel_transaction_status import FuelTransactionStatus
from app.domain.enums.fuel_station_type import FuelStationType
from app.domain.enums.fuel_type import FuelType
from app.domain.enums.fuel_payment_mode import FuelPaymentMode
from app.domain.exceptions.fuel import (
    FuelValidationException,
    FuelCapacityExceededException,
    FuelOdometerException,
    FuelDuplicateException,
    FuelVendorNotFoundException
)
from app.application.dtos.fuel import FuelTransactionCreate, FuelTransactionUpdate
from app.application.services.fuel_service import FuelService


@pytest.fixture
def mock_repositories():
    return {
        "repository": AsyncMock(),
        "vendor_repository": AsyncMock(),
        "tractor_repository": AsyncMock(),
        "driver_repository": AsyncMock(),
        "trip_repository": AsyncMock(),
        "expense_repository": AsyncMock(),
        "session": AsyncMock()
    }


@pytest.fixture
def fuel_service(mock_repositories):
    return FuelService(**mock_repositories)


@pytest.mark.asyncio
async def test_create_transaction_success(fuel_service, mock_repositories):
    # Setup mocks
    mock_repositories["repository"].check_duplicate.return_value = False
    
    mock_vendor = FuelVendor(id=uuid.uuid4(), is_active=True)
    mock_repositories["vendor_repository"].get_by_id.return_value = mock_vendor
    
    mock_tractor = Tractor(id=uuid.uuid4(), fuel_capacity=100)
    mock_repositories["tractor_repository"].get_by_id.return_value = mock_tractor
    
    mock_repositories["repository"].get_previous_transaction.return_value = None
    mock_repositories["repository"].get_latest_odometer.return_value = 1000
    
    mock_tx = FuelTransaction(id=uuid.uuid4(), fuel_number="FUEL-20231015-001")
    mock_repositories["repository"].create.return_value = mock_tx

    with patch("app.application.services.fuel_service.FuelNumberGenerator.generate", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "FUEL-20231015-001"
        
        data = FuelTransactionCreate(
            tractor_id=mock_tractor.id,
            driver_id=uuid.uuid4(),
            vendor_id=mock_vendor.id,
            station_type=FuelStationType.REGULAR,
            fuel_type=FuelType.DIESEL,
            fuel_date=date.today(),
            odometer=1200,
            liters=Decimal("50.0"),
            rate_per_liter=Decimal("90.0"),
            amount=Decimal("4500.0"),
            payment_mode=FuelPaymentMode.CASH
        )
        
        result = await fuel_service.create_transaction(data, created_by=uuid.uuid4())
        
        assert result == mock_tx
        mock_repositories["repository"].create.assert_called_once()


@pytest.mark.asyncio
async def test_create_transaction_capacity_exceeded(fuel_service, mock_repositories):
    mock_repositories["repository"].check_duplicate.return_value = False
    
    mock_vendor = FuelVendor(id=uuid.uuid4(), is_active=True)
    mock_repositories["vendor_repository"].get_by_id.return_value = mock_vendor
    
    mock_tractor = Tractor(id=uuid.uuid4(), fuel_capacity=100)
    mock_repositories["tractor_repository"].get_by_id.return_value = mock_tractor
    
    data = FuelTransactionCreate(
        tractor_id=mock_tractor.id,
        driver_id=uuid.uuid4(),
        vendor_id=mock_vendor.id,
        station_type=FuelStationType.REGULAR,
        fuel_type=FuelType.DIESEL,
        fuel_date=date.today(),
        odometer=1200,
        liters=Decimal("150.0"), # Exceeds capacity
        rate_per_liter=Decimal("90.0"),
        amount=Decimal("13500.0"),
        payment_mode=FuelPaymentMode.CASH
    )
    
    with pytest.raises(FuelCapacityExceededException):
        await fuel_service.create_transaction(data, created_by=uuid.uuid4())


@pytest.mark.asyncio
async def test_calculate_kmpl_valid(fuel_service, mock_repositories):
    mock_prev_tx = FuelTransaction(id=uuid.uuid4(), odometer=1000)
    mock_repositories["repository"].get_previous_transaction.return_value = mock_prev_tx
    
    prev_odo, dist, kmpl = await fuel_service._calculate_kmpl_and_distance(
        uuid.uuid4(), date.today(), 1500, Decimal("50.0")
    )
    
    assert prev_odo == 1000
    assert dist == 500
    assert kmpl == Decimal("10.0")


@pytest.mark.asyncio
async def test_calculate_kmpl_invalid_odometer(fuel_service, mock_repositories):
    mock_prev_tx = FuelTransaction(id=uuid.uuid4(), odometer=1500)
    mock_repositories["repository"].get_previous_transaction.return_value = mock_prev_tx
    
    with pytest.raises(FuelOdometerException):
        await fuel_service._calculate_kmpl_and_distance(
            uuid.uuid4(), date.today(), 1000, Decimal("50.0")
        )
