from datetime import date, datetime, timezone
from typing import Sequence
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.application.dtos.trip import TripCreate, TripUpdate
from app.application.services.trip_number_generator import TripNumberGenerator
from app.domain.entities.trip import Trip
from app.domain.entities.trip_status_history import TripStatusHistory
from app.domain.entities.driver import Driver
from app.domain.entities.tractor import Tractor
from app.domain.entities.party import Party
from app.domain.enums.trip_status import TripStatus
from app.domain.enums.driver_status import DriverStatus
from app.domain.exceptions.driver import DriverNotFoundException
from app.domain.exceptions.tractor import TractorNotFoundException
from app.domain.exceptions.party import PartyNotFoundException
from app.domain.exceptions.trip import (
    TripNotFoundException,
    TripAlreadyExistsException,
    TripStatusException,
    DriverBusyException,
    TractorBusyException,
    TripDeleteException,
    InactiveDriverException,
    InactiveTractorException,
    InactivePartyException,
    InvalidTripDateException,
    AdvanceAmountException,
    TripAlreadyCompletedException,
)
from app.domain.repositories.trip_repository import TripRepository


class TripService:
    """
    Application Service layer orchestrating business workflows and domain validation rules
    for the Trip entity.
    """

    def __init__(self, session: AsyncSession, repository: TripRepository) -> None:
        self.session = session
        self.repository = repository
        self.generator = TripNumberGenerator(repository)

    async def create_trip(self, dto: TripCreate, current_user_id: uuid.UUID) -> Trip:
        """
        Registers a new Trip transaction after verifying driver/tractor locks and entity states.
        Raises DriverBusyException, TractorBusyException, and InactiveAsset exceptions.
        """
        # 1. Verify Party exists and is active
        party = await self.session.get(Party, dto.party_id)
        if not party or party.deleted_at is not None:
            raise PartyNotFoundException(dto.party_id)
        if not party.is_active:
            raise InactivePartyException(dto.party_id)

        # 2. Verify Tractor exists and is active
        tractor = await self.session.get(Tractor, dto.tractor_id)
        if not tractor or tractor.deleted_at is not None:
            raise TractorNotFoundException(dto.tractor_id)
        if not tractor.is_active:
            raise InactiveTractorException(dto.tractor_id)
        if tractor.current_trip_id is not None:
            raise TractorBusyException(dto.tractor_id)

        # 3. Verify Driver exists and is active
        driver = await self.session.get(Driver, dto.driver_id)
        if not driver or driver.deleted_at is not None:
            raise DriverNotFoundException(dto.driver_id)
        if not driver.is_active:
            raise InactiveDriverException(dto.driver_id)
        if driver.current_trip_id is not None or driver.current_status == DriverStatus.ON_TRIP:
            raise DriverBusyException(dto.driver_id)

        # 4. Auto-generate Trip Number
        trip_num = await self.generator.generate()

        # 5. Construct domain model
        trip = Trip(
            trip_number=trip_num,
            party_id=dto.party_id,
            tractor_id=dto.tractor_id,
            driver_id=dto.driver_id,
            source_location=dto.source_location,
            destination_location=dto.destination_location,
            trip_date=dto.trip_date,
            expected_delivery_date=dto.expected_delivery_date,
            freight_amount=dto.freight_amount,
            advance_amount=dto.advance_amount,
            remarks=dto.remarks,
            status=TripStatus.PENDING,
            created_by=current_user_id,
            updated_by=current_user_id,
            is_active=True,
        )

        await self.repository.create(trip)
        await self.session.flush() # Yields trip.id for status logs

        # 6. Apply asset locks
        driver.current_trip_id = trip.id
        tractor.current_trip_id = trip.id

        # 7. Record status transition history
        history = TripStatusHistory(
            trip_id=trip.id,
            old_status=None,
            new_status=TripStatus.PENDING.value,
            remarks="Trip record created.",
            created_by=current_user_id,
            updated_by=current_user_id,
            is_active=True,
        )
        self.session.add(history)

        await self.session.commit()
        return trip

    async def get_trip_by_id(self, trip_id: uuid.UUID) -> Trip:
        """
        Loads a single active trip by ID.
        Raises TripNotFoundException if not found.
        """
        trip = await self.repository.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundException(trip_id)
        return trip

    async def update_trip(self, trip_id: uuid.UUID, dto: TripUpdate, current_user_id: uuid.UUID) -> Trip:
        """
        Updates an existing Trip transaction.
        Enforces status editing blocks:
        - Locks completed or cancelled trips.
        - Limits updates to remarks and expected delivery dates for dispatched or in-progress trips.
        """
        trip = await self.repository.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundException(trip_id)

        # 1. completed or cancelled blocks
        if trip.status in [TripStatus.COMPLETED, TripStatus.CANCELLED]:
            raise TripAlreadyCompletedException(trip_id)

        # 2. dispatched or in-progress blocks (only remarks/delivery date updates allowed)
        if trip.status in [TripStatus.DISPATCHED, TripStatus.IN_PROGRESS]:
            # Scan for unauthorized field updates
            has_forbidden_updates = any([
                dto.party_id is not None,
                dto.tractor_id is not None,
                dto.driver_id is not None,
                dto.source_location is not None,
                dto.destination_location is not None,
                dto.trip_date is not None,
                dto.freight_amount is not None,
                dto.advance_amount is not None,
                dto.is_active is not None
            ])
            if has_forbidden_updates:
                raise TripStatusException("Dispatched or In Progress trips can only update remarks or expected delivery date.")

        # 3. Process authorized edits
        if dto.remarks is not None:
            trip.remarks = dto.remarks
        if dto.expected_delivery_date is not None:
            if dto.expected_delivery_date < trip.trip_date:
                raise InvalidTripDateException("Expected delivery date cannot be before the trip date.")
            trip.expected_delivery_date = dto.expected_delivery_date

        # Processing other fields if trip is PENDING
        if trip.status == TripStatus.PENDING:
            if dto.party_id is not None and dto.party_id != trip.party_id:
                party = await self.session.get(Party, dto.party_id)
                if not party or party.deleted_at is not None:
                    raise PartyNotFoundException(dto.party_id)
                if not party.is_active:
                    raise InactivePartyException(dto.party_id)
                trip.party_id = dto.party_id

            if dto.tractor_id is not None and dto.tractor_id != trip.tractor_id:
                # Release old tractor lock
                old_tractor = await self.session.get(Tractor, trip.tractor_id)
                if old_tractor:
                    old_tractor.current_trip_id = None

                new_tractor = await self.session.get(Tractor, dto.tractor_id)
                if not new_tractor or new_tractor.deleted_at is not None:
                    raise TractorNotFoundException(dto.tractor_id)
                if not new_tractor.is_active:
                    raise InactiveTractorException(dto.tractor_id)
                if new_tractor.current_trip_id is not None:
                    raise TractorBusyException(dto.tractor_id)
                new_tractor.current_trip_id = trip.id
                trip.tractor_id = dto.tractor_id

            if dto.driver_id is not None and dto.driver_id != trip.driver_id:
                # Release old driver lock
                old_driver = await self.session.get(Driver, trip.driver_id)
                if old_driver:
                    old_driver.current_trip_id = None
                    old_driver.current_status = DriverStatus.AVAILABLE

                new_driver = await self.session.get(Driver, dto.driver_id)
                if not new_driver or new_driver.deleted_at is not None:
                    raise DriverNotFoundException(dto.driver_id)
                if not new_driver.is_active:
                    raise InactiveDriverException(dto.driver_id)
                if new_driver.current_trip_id is not None:
                    raise DriverBusyException(dto.driver_id)
                new_driver.current_trip_id = trip.id
                trip.driver_id = dto.driver_id

            if dto.source_location is not None:
                trip.source_location = dto.source_location
            if dto.destination_location is not None:
                trip.destination_location = dto.destination_location
            if dto.trip_date is not None:
                trip.trip_date = dto.trip_date

            # Amounts checking
            new_freight = dto.freight_amount if dto.freight_amount is not None else trip.freight_amount
            new_advance = dto.advance_amount if dto.advance_amount is not None else trip.advance_amount
            if new_advance > new_freight:
                raise AdvanceAmountException("Advance amount cannot exceed the freight amount.")

            if dto.freight_amount is not None:
                trip.freight_amount = dto.freight_amount
            if dto.advance_amount is not None:
                trip.advance_amount = dto.advance_amount

        trip.updated_by = current_user_id
        trip.updated_at = datetime.now(timezone.utc)

        await self.repository.update(trip)
        await self.session.commit()
        return trip

    async def update_trip_status(
        self,
        trip_id: uuid.UUID,
        new_status: TripStatus,
        remarks: str | None,
        current_user_id: uuid.UUID,
    ) -> Trip:
        """
        Manages workflow state shifts for a Trip, checking transitions bounds and locking/unlocking assets.
        """
        trip = await self.repository.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundException(trip_id)

        old_status = trip.status

        # 1. Validate status transition pathways
        valid_transitions = {
            TripStatus.PENDING: [TripStatus.DISPATCHED, TripStatus.CANCELLED],
            TripStatus.DISPATCHED: [TripStatus.IN_PROGRESS, TripStatus.CANCELLED],
            TripStatus.IN_PROGRESS: [TripStatus.COMPLETED, TripStatus.CANCELLED],
            TripStatus.COMPLETED: [],
            TripStatus.CANCELLED: [],
        }

        if new_status not in valid_transitions[old_status]:
            raise TripStatusException(f"Invalid transition from status {old_status} to {new_status}.")

        driver = await self.session.get(Driver, trip.driver_id)
        tractor = await self.session.get(Tractor, trip.tractor_id)

        # 2. Toggle locks based on status shifting
        if new_status == TripStatus.DISPATCHED:
            if driver:
                driver.current_status = DriverStatus.ON_TRIP
        elif new_status == TripStatus.COMPLETED:
            if driver:
                driver.current_trip_id = None
                driver.current_status = DriverStatus.AVAILABLE
            if tractor:
                tractor.current_trip_id = None
            trip.actual_delivery_date = date.today()
        elif new_status == TripStatus.CANCELLED:
            if driver:
                driver.current_trip_id = None
                driver.current_status = DriverStatus.AVAILABLE
            if tractor:
                tractor.current_trip_id = None

        trip.status = new_status
        trip.updated_by = current_user_id
        trip.updated_at = datetime.now(timezone.utc)

        # 3. Log shift history
        history = TripStatusHistory(
            trip_id=trip.id,
            old_status=old_status.value,
            new_status=new_status.value,
            remarks=remarks,
            created_by=current_user_id,
            updated_by=current_user_id,
            is_active=True,
        )
        self.session.add(history)

        await self.repository.update(trip)
        await self.session.commit()
        return trip

    async def delete_trip(self, trip_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """
        Soft-deletes a Trip profile.
        Allowed strictly if trip status is PENDING and no downstream items exist.
        """
        trip = await self.repository.get_by_id(trip_id)
        if not trip:
            raise TripNotFoundException(trip_id)

        # 1. Enforce status constraints
        if trip.status != TripStatus.PENDING:
            raise TripDeleteException(f"Trips with status {trip.status} cannot be deleted. Only PENDING trips can be deleted.")

        # 2. Enforce downstream integrations constraints
        if await self.repository.has_expenses(trip_id):
            raise TripDeleteException("Trip cannot be deleted because it is linked with expenses.")
        if await self.repository.has_invoice(trip_id):
            raise TripDeleteException("Trip cannot be deleted because it has a registered invoice.")
        if await self.repository.has_settlement(trip_id):
            raise TripDeleteException("Trip cannot be deleted because it has settlements pending.")

        driver = await self.session.get(Driver, trip.driver_id)
        tractor = await self.session.get(Tractor, trip.tractor_id)

        # 3. Release asset locks
        if driver:
            driver.current_trip_id = None
            driver.current_status = DriverStatus.AVAILABLE
        if tractor:
            tractor.current_trip_id = None

        trip.updated_by = current_user_id
        trip.updated_at = datetime.now(timezone.utc)
        trip.is_active = False

        await self.repository.delete(trip_id, soft=True)
        await self.session.commit()
        return True

    async def get_trip_history(self, trip_id: uuid.UUID) -> Sequence[TripStatusHistory]:
        """
        Loads the history of status logs for a trip.
        """
        stmt = select(TripStatusHistory).where(
            TripStatusHistory.trip_id == trip_id,
            TripStatusHistory.deleted_at.is_(None)
        ).order_by(TripStatusHistory.created_at.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def paginate_trips(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        status_filter: str | None = None,
        driver_id: uuid.UUID | None = None,
        party_id: uuid.UUID | None = None,
        tractor_id: uuid.UUID | None = None,
        date_start: str | None = None,
        date_end: str | None = None,
        created_date_start: str | None = None,
        created_date_end: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Trip], int]:
        """
        Fetches a paginated page of trips matching filters.
        """
        return await self.repository.get_trips(
            page=page,
            size=size,
            search_query=search_query,
            status_filter=status_filter,
            driver_id=driver_id,
            party_id=party_id,
            tractor_id=tractor_id,
            date_start=date_start,
            date_end=date_end,
            created_date_start=created_date_start,
            created_date_end=created_date_end,
            sort_by=sort_by,
            order=order,
            include_deleted=include_deleted,
        )
