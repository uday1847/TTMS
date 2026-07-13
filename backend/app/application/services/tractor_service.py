from datetime import datetime, timezone
from typing import Sequence
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.tractor import TractorCreate, TractorUpdate
from app.domain.entities.tractor import Tractor
from app.domain.exceptions.tractor import (
    TractorAlreadyExistsException,
    TractorHasActiveTripsException,
    TractorNotFoundException,
)
from app.domain.repositories.tractor_repository import TractorRepository


class TractorService:
    """
    Application Service layer orchestrating business workflows and domain rules
    for the Tractor entity.
    """

    def __init__(self, session: AsyncSession, repository: TractorRepository) -> None:
        self.session = session
        self.repository = repository

    async def create_tractor(self, dto: TractorCreate, current_user_id: uuid.UUID) -> Tractor:
        """
        Creates a new tractor asset record after validating business constraints.
        Raises TractorAlreadyExistsException if tractor plate or RC number is already in use.
        """
        # Validate unique tractor plate number
        existing_plate = await self.repository.get_by_tractor_number(dto.tractor_number)
        if existing_plate:
            raise TractorAlreadyExistsException(f"Tractor number '{dto.tractor_number}' is already registered.")

        # Validate unique Registration Certificate number
        existing_rc = await self.repository.get_by_rc_number(dto.rc_number)
        if existing_rc:
            raise TractorAlreadyExistsException(f"RC number '{dto.rc_number}' is already registered.")

        # Construct domain model
        tractor = Tractor(
            tractor_number=dto.tractor_number,
            owner_name=dto.owner_name,
            rc_number=dto.rc_number,
            insurance_number=dto.insurance_number,
            insurance_expiry=dto.insurance_expiry,
            manufacturer=dto.manufacturer,
            model=dto.model,
            registration_date=dto.registration_date,
            remarks=dto.remarks,
            created_by=current_user_id,
            updated_by=current_user_id,
            is_active=True,
        )

        await self.repository.create(tractor)
        await self.session.commit()
        return tractor

    async def get_tractor_by_id(self, tractor_id: uuid.UUID) -> Tractor:
        """
        Loads a single active tractor by ID.
        Raises TractorNotFoundException if not found.
        """
        tractor = await self.repository.get_by_id(tractor_id)
        if not tractor:
            raise TractorNotFoundException(tractor_id)
        return tractor

    async def get_all_tractors(self) -> Sequence[Tractor]:
        """
        Returns all active tractors.
        """
        return await self.repository.get_all()

    async def update_tractor(self, tractor_id: uuid.UUID, dto: TractorUpdate, current_user_id: uuid.UUID) -> Tractor:
        """
        Updates an existing tractor profile.
        Validates unique constraints on changed values.
        Raises TractorNotFoundException or TractorAlreadyExistsException.
        """
        tractor = await self.repository.get_by_id(tractor_id)
        if not tractor:
            raise TractorNotFoundException(tractor_id)

        # Validation on updated tractor plate number
        if dto.tractor_number is not None and dto.tractor_number != tractor.tractor_number:
            existing = await self.repository.get_by_tractor_number(dto.tractor_number)
            if existing:
                raise TractorAlreadyExistsException(f"Tractor number '{dto.tractor_number}' is already registered.")
            tractor.tractor_number = dto.tractor_number

        # Validation on updated RC number
        if dto.rc_number is not None and dto.rc_number != tractor.rc_number:
            existing = await self.repository.get_by_rc_number(dto.rc_number)
            if existing:
                raise TractorAlreadyExistsException(f"RC number '{dto.rc_number}' is already registered.")
            tractor.rc_number = dto.rc_number

        # Update nullable and standard values if provided in request
        if dto.owner_name is not None:
            tractor.owner_name = dto.owner_name
        if dto.insurance_number is not None:
            tractor.insurance_number = dto.insurance_number
        if dto.insurance_expiry is not None:
            tractor.insurance_expiry = dto.insurance_expiry
        if dto.manufacturer is not None:
            tractor.manufacturer = dto.manufacturer
        if dto.model is not None:
            tractor.model = dto.model
        if dto.registration_date is not None:
            tractor.registration_date = dto.registration_date
        if dto.remarks is not None:
            tractor.remarks = dto.remarks
        if dto.is_active is not None:
            tractor.is_active = dto.is_active

        # Audit stamping
        tractor.updated_by = current_user_id
        tractor.updated_at = datetime.now(timezone.utc)

        await self.repository.update(tractor)
        await self.session.commit()
        return tractor

    async def delete_tractor(self, tractor_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """
        Soft-deletes a tractor.
        Raises TractorNotFoundException or TractorHasActiveTripsException.
        """
        tractor = await self.repository.get_by_id(tractor_id)
        if not tractor:
            raise TractorNotFoundException(tractor_id)

        # Integrity check: verify active trips constraints
        has_trips = await self.repository.has_active_trips(tractor_id)
        if has_trips:
            raise TractorHasActiveTripsException(tractor_id)

        # Stamp audit details before marking as soft-deleted
        tractor.updated_by = current_user_id
        tractor.updated_at = datetime.now(timezone.utc)
        tractor.is_active = False

        await self.repository.delete(tractor_id, soft=True)
        await self.session.commit()
        return True

    async def paginate_tractors(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        status_filter: str | None = None,
        insurance_expiring_days: int | None = None,
        created_date_start: str | None = None,
        created_date_end: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Tractor], int]:
        """
        Fetches a paginated page of tractors matching search, sort, and status parameters.
        """
        return await self.repository.get_tractors(
            page=page,
            size=size,
            search_query=search_query,
            status_filter=status_filter,
            insurance_expiring_days=insurance_expiring_days,
            created_date_start=created_date_start,
            created_date_end=created_date_end,
            sort_by=sort_by,
            order=order,
            include_deleted=include_deleted,
        )
