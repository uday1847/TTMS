from datetime import datetime, timezone
from typing import Sequence
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.driver import DriverCreate, DriverUpdate
from app.domain.entities.driver import Driver
from app.domain.enums.driver_status import DriverStatus
from app.domain.exceptions.driver import (
    DriverAlreadyExistsException,
    DriverHasActiveTripsException,
    DriverNotFoundException,
)
from app.domain.repositories.driver_repository import DriverRepository


class DriverService:
    """
    Application Service layer orchestrating business workflows and domain rules
    for the Driver entity.
    """

    def __init__(self, session: AsyncSession, repository: DriverRepository) -> None:
        self.session = session
        self.repository = repository

    async def create_driver(self, *, dto: DriverCreate, current_user_id: uuid.UUID) -> Driver:
        """
        Creates a new driver record after validating business constraints.
        Raises DriverAlreadyExistsException if employee code, license, or phone is already in use.
        """
        # Validate unique employee code
        existing_code = await self.repository.get_by_employee_code(dto.employee_code)
        if existing_code:
            raise DriverAlreadyExistsException(f"Employee code '{dto.employee_code}' is already registered.")

        # Validate unique license number
        existing_license = await self.repository.get_by_license_number(dto.license_number)
        if existing_license:
            raise DriverAlreadyExistsException(f"Driving license '{dto.license_number}' is already registered.")

        # Validate unique contact phone
        existing_phone = await self.repository.get_by_contact_phone(dto.contact_phone)
        if existing_phone:
            raise DriverAlreadyExistsException(f"Mobile number '{dto.contact_phone}' is already registered.")

        # Construct domain model
        driver = Driver(
            name=dto.name,
            address=dto.address,
            user_id=dto.user_id,
            employee_code=dto.employee_code,
            license_number=dto.license_number,
            license_expiry=dto.license_expiry,
            license_class=dto.license_class,
            contact_phone=dto.contact_phone,
            emergency_contact_phone=dto.emergency_contact_phone,
            fixed_salary=dto.fixed_salary,
            commission_percentage=dto.commission_percentage,
            driver_type=dto.driver_type,
            current_status=dto.current_status,
            created_by=current_user_id,
            updated_by=current_user_id,
            is_active=True,
        )

        await self.repository.create(driver)
        await self.session.commit()
        return driver

    async def get_driver_by_id(self, driver_id: uuid.UUID) -> Driver:
        """
        Loads a single active driver.
        Raises DriverNotFoundException if not found.
        """
        driver = await self.repository.get_by_id(driver_id)
        if not driver:
            raise DriverNotFoundException(driver_id)
        return driver

    async def get_all_drivers(self) -> Sequence[Driver]:
        """
        Returns all active drivers.
        """
        return await self.repository.get_all()

    async def update_driver(self, *, driver_id: uuid.UUID, dto: DriverUpdate, current_user_id: uuid.UUID) -> Driver:
        """
        Updates an existing driver profile.
        Validates unique constraints on changed values.
        Raises DriverNotFoundException or DriverAlreadyExistsException.
        """
        driver = await self.repository.get_by_id(driver_id)
        if not driver:
            raise DriverNotFoundException(driver_id)

        # Validation on updated employee code
        if dto.employee_code is not None and dto.employee_code != driver.employee_code:
            existing = await self.repository.get_by_employee_code(dto.employee_code)
            if existing:
                raise DriverAlreadyExistsException(f"Employee code '{dto.employee_code}' is already registered.")
            driver.employee_code = dto.employee_code

        # Validation on updated license number
        if dto.license_number is not None and dto.license_number != driver.license_number:
            existing = await self.repository.get_by_license_number(dto.license_number)
            if existing:
                raise DriverAlreadyExistsException(f"Driving license '{dto.license_number}' is already registered.")
            driver.license_number = dto.license_number

        # Validation on updated contact phone
        if dto.contact_phone is not None and dto.contact_phone != driver.contact_phone:
            existing = await self.repository.get_by_contact_phone(dto.contact_phone)
            if existing:
                raise DriverAlreadyExistsException(f"Mobile number '{dto.contact_phone}' is already registered.")
            driver.contact_phone = dto.contact_phone

        # Update nullable and standard values if provided in request
        if dto.name is not None:
            driver.name = dto.name
        if dto.address is not None:
            driver.address = dto.address
        if dto.user_id is not None:
            driver.user_id = dto.user_id
        if dto.license_expiry is not None:
            driver.license_expiry = dto.license_expiry
        if dto.license_class is not None:
            driver.license_class = dto.license_class
        if dto.emergency_contact_phone is not None:
            driver.emergency_contact_phone = dto.emergency_contact_phone
        if dto.fixed_salary is not None:
            driver.fixed_salary = dto.fixed_salary
        if dto.commission_percentage is not None:
            driver.commission_percentage = dto.commission_percentage
        if dto.driver_type is not None:
            driver.driver_type = dto.driver_type
        if dto.current_status is not None:
            driver.current_status = dto.current_status
        if dto.is_active is not None:
            driver.is_active = dto.is_active
            if not dto.is_active:
                driver.current_status = DriverStatus.INACTIVE

        # Audit stamping
        driver.updated_by = current_user_id
        driver.updated_at = datetime.now(timezone.utc)

        await self.repository.update(driver)
        await self.session.commit()
        return driver

    async def delete_driver(self, *, driver_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """
        Soft-deletes a driver.
        Raises DriverNotFoundException or DriverHasActiveTripsException.
        """
        driver = await self.repository.get_by_id(driver_id)
        if not driver:
            raise DriverNotFoundException(driver_id)

        # Integrity check: verify active trips constraints
        has_trips = await self.repository.has_active_trips(driver_id)
        if has_trips:
            raise DriverHasActiveTripsException(driver_id)

        # Stamp audit details before marking as soft-deleted
        driver.updated_by = current_user_id
        driver.updated_at = datetime.now(timezone.utc)

        await self.repository.delete(driver_id, soft=True)
        await self.session.commit()
        return True

    async def paginate_drivers(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        status_filter: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Driver], int]:
        """
        Fetches a paginated page of drivers matching search, sort, and status parameters.
        """
        return await self.repository.get_drivers(
            page=page,
            size=size,
            search_query=search_query,
            status_filter=status_filter,
            sort_by=sort_by,
            order=order,
            include_deleted=include_deleted,
        )
