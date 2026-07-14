import uuid
from decimal import Decimal
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.fuel_transaction import FuelTransaction
from app.domain.entities.fuel_history import FuelHistory
from app.domain.entities.trip_expense import TripExpense
from app.domain.enums.expense_type import ExpenseType
from app.domain.enums.fuel_transaction_status import FuelTransactionStatus
from app.domain.exceptions.fuel import (
    FuelTransactionNotFoundException,
    FuelValidationException,
    FuelCapacityExceededException,
    FuelOdometerException,
    FuelDuplicateException,
    FuelVendorNotFoundException
)
from app.domain.repositories.fuel_repository import FuelRepository
from app.domain.repositories.fuel_vendor_repository import FuelVendorRepository
from app.domain.repositories.tractor_repository import TractorRepository
from app.domain.repositories.driver_repository import DriverRepository
from app.domain.repositories.trip_repository import TripRepository
from app.domain.repositories.trip_expense_repository import TripExpenseRepository
from app.application.dtos.fuel import FuelTransactionCreate, FuelTransactionUpdate
from app.application.services.fuel_number_generator import FuelNumberGenerator


class FuelService:
    def __init__(
        self,
        repository: FuelRepository,
        vendor_repository: FuelVendorRepository,
        tractor_repository: TractorRepository,
        driver_repository: DriverRepository,
        trip_repository: TripRepository,
        expense_repository: TripExpenseRepository,
        session: AsyncSession
    ):
        self.repository = repository
        self.vendor_repository = vendor_repository
        self.tractor_repository = tractor_repository
        self.driver_repository = driver_repository
        self.trip_repository = trip_repository
        self.expense_repository = expense_repository
        self.session = session

    async def _calculate_kmpl_and_distance(self, tractor_id: uuid.UUID, fuel_date: date, current_odometer: int, liters: Decimal) -> tuple[Optional[int], Optional[int], Optional[Decimal]]:
        previous_tx = await self.repository.get_previous_transaction(tractor_id, fuel_date)
        if previous_tx:
            prev_odo = previous_tx.odometer
            distance = current_odometer - prev_odo
            if distance < 0:
                raise FuelOdometerException("Current odometer must be greater than or equal to previous odometer.")
            
            # calculate kmpl based on distance / liters of current fill
            if liters > 0:
                average_kmpl = Decimal(distance) / liters
            else:
                average_kmpl = None
                
            return prev_odo, distance, average_kmpl
        
        return None, None, None

    async def create_transaction(self, data: FuelTransactionCreate, created_by: uuid.UUID) -> FuelTransaction:
        # Check duplicate
        is_duplicate = await self.repository.check_duplicate(
            data.tractor_id, data.vendor_id, data.fuel_date, float(data.amount), float(data.liters)
        )
        if is_duplicate:
            raise FuelDuplicateException()

        # Validate vendor
        vendor = await self.vendor_repository.get_by_id(data.vendor_id)
        if not vendor:
            raise FuelVendorNotFoundException()
        if not vendor.is_active:
            raise FuelValidationException("Fuel vendor is not active.")

        # Validate tractor and capacity
        tractor = await self.tractor_repository.get_by_id(data.tractor_id)
        if not tractor:
            raise FuelValidationException("Tractor not found.")
        if tractor.fuel_capacity and data.liters > tractor.fuel_capacity:
            raise FuelCapacityExceededException()

        # Generate fuel number
        date_str = datetime.utcnow().strftime("%Y%m%d")
        fuel_number = await FuelNumberGenerator.generate(self.session, date_str)

        # Calculate KMPL
        prev_odo, dist, kmpl = await self._calculate_kmpl_and_distance(data.tractor_id, data.fuel_date, data.odometer, data.liters)

        # Sync tractor odometer if this is the newest record
        latest_odo = await self.repository.get_latest_odometer(data.tractor_id)
        if data.odometer > latest_odo:
            tractor.current_odometer = data.odometer
            await self.tractor_repository.update(tractor)

        transaction = FuelTransaction(
            fuel_number=fuel_number,
            tractor_id=data.tractor_id,
            trip_id=data.trip_id,
            driver_id=data.driver_id,
            vendor_id=data.vendor_id,
            station_type=data.station_type,
            fuel_type=data.fuel_type,
            fuel_date=data.fuel_date,
            odometer=data.odometer,
            liters=data.liters,
            rate_per_liter=data.rate_per_liter,
            amount=data.amount,
            previous_odometer=prev_odo,
            distance_since_last_fill=dist,
            average_kmpl=kmpl,
            payment_mode=data.payment_mode,
            invoice_number=data.invoice_number,
            remarks=data.remarks,
            attachment=data.attachment,
            latitude=data.latitude,
            longitude=data.longitude,
            is_full_tank=data.is_full_tank,
            fuel_card_number=data.fuel_card_number,
            authorization_code=data.authorization_code,
            transaction_reference=data.transaction_reference,
            gps_latitude=data.gps_latitude,
            gps_longitude=data.gps_longitude,
            gps_accuracy=data.gps_accuracy,
            device_id=data.device_id,
            location_address=data.location_address,
            status=FuelTransactionStatus.DRAFT,
            created_by=created_by,
            updated_by=created_by,
        )

        transaction = await self.repository.create(transaction)

        # Auto-create TripExpense if linked to a Trip
        if data.trip_id:
            await self._create_linked_expense(transaction, created_by)

        return transaction

    async def _create_linked_expense(self, transaction: FuelTransaction, created_by: uuid.UUID):
        from app.application.services.expense_number_generator import ExpenseNumberGenerator
        trip = await self.trip_repository.get_by_id(transaction.trip_id)
        if trip:
            expense_number = await ExpenseNumberGenerator.generate(self.session, trip.trip_number)
            expense = TripExpense(
                expense_number=expense_number,
                trip_id=trip.id,
                expense_type=ExpenseType.FUEL,
                amount=transaction.amount,
                expense_date=transaction.fuel_date,
                payment_mode=transaction.payment_mode,
                description=f"Auto-generated for fuel transaction {transaction.fuel_number}",
                created_by=created_by,
                updated_by=created_by,
            )
            await self.expense_repository.create(expense)

    async def get_transaction(self, transaction_id: uuid.UUID) -> FuelTransaction:
        tx = await self.repository.get_by_id(transaction_id)
        if not tx:
            raise FuelTransactionNotFoundException()
        return tx

    async def get_transactions(
        self,
        skip: int = 0,
        limit: int = 100,
        tractor_id: Optional[uuid.UUID] = None,
        trip_id: Optional[uuid.UUID] = None,
        vendor_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[FuelTransaction]:
        return await self.repository.get_all(skip, limit, tractor_id, trip_id, vendor_id, status, start_date, end_date)

    async def count_transactions(
        self,
        tractor_id: Optional[uuid.UUID] = None,
        trip_id: Optional[uuid.UUID] = None,
        vendor_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        return await self.repository.count(tractor_id, trip_id, vendor_id, status, start_date, end_date)

    async def update_transaction(self, transaction_id: uuid.UUID, data: FuelTransactionUpdate, updated_by: uuid.UUID) -> FuelTransaction:
        tx = await self.get_transaction(transaction_id)

        if tx.status in [FuelTransactionStatus.CANCELLED, FuelTransactionStatus.APPROVED]:
            raise FuelValidationException("Cannot update an approved or cancelled transaction.")

        # Create history record
        history = FuelHistory(
            fuel_transaction_id=tx.id,
            old_amount=tx.amount,
            new_amount=data.amount if data.amount is not None else tx.amount,
            old_odometer=tx.odometer,
            new_odometer=data.odometer if data.odometer is not None else tx.odometer,
            old_vendor_id=tx.vendor_id,
            new_vendor_id=data.vendor_id if data.vendor_id is not None else tx.vendor_id,
            old_status=tx.status,
            new_status=tx.status,
            reason=data.update_reason,
            edited_by=updated_by
        )
        await self.repository.add_history(history)

        update_data = data.model_dump(exclude_unset=True, exclude={"update_reason"})
        
        # If odometer or liters or tractor changes, recalculate KMPL
        needs_recalc = any(k in update_data for k in ['odometer', 'liters', 'tractor_id', 'fuel_date'])
        
        for field, value in update_data.items():
            setattr(tx, field, value)

        if needs_recalc:
            prev_odo, dist, kmpl = await self._calculate_kmpl_and_distance(tx.tractor_id, tx.fuel_date, tx.odometer, tx.liters)
            tx.previous_odometer = prev_odo
            tx.distance_since_last_fill = dist
            tx.average_kmpl = kmpl

            # Update tractor odometer
            latest_odo = await self.repository.get_latest_odometer(tx.tractor_id)
            if tx.odometer > latest_odo:
                tractor = await self.tractor_repository.get_by_id(tx.tractor_id)
                if tractor:
                    tractor.current_odometer = tx.odometer
                    await self.tractor_repository.update(tractor)

        tx.updated_by = updated_by
        return await self.repository.update(tx)

    async def change_status(self, transaction_id: uuid.UUID, new_status: FuelTransactionStatus, updated_by: uuid.UUID, reason: str = "Status update") -> FuelTransaction:
        tx = await self.get_transaction(transaction_id)
        
        history = FuelHistory(
            fuel_transaction_id=tx.id,
            old_status=tx.status,
            new_status=new_status,
            reason=reason,
            edited_by=updated_by
        )
        await self.repository.add_history(history)

        tx.status = new_status
        tx.updated_by = updated_by
        return await self.repository.update(tx)
