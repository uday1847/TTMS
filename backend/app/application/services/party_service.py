from datetime import datetime, timezone
from typing import Sequence
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.party import PartyCreate, PartyUpdate
from app.domain.entities.party import Party
from app.domain.exceptions.party import (
    PartyAlreadyExistsException,
    PartyHasActiveTripsException,
    PartyNotFoundException,
)
from app.domain.repositories.party_repository import PartyRepository


class PartyService:
    """
    Application Service layer orchestrating business workflows and domain rules
    for the Party entity.
    """

    def __init__(self, session: AsyncSession, repository: PartyRepository) -> None:
        self.session = session
        self.repository = repository

    async def create_party(self, dto: PartyCreate, current_user_id: uuid.UUID) -> Party:
        """
        Creates a new party record after validating business constraints.
        Raises PartyAlreadyExistsException if unique constraints are violated.
        """
        # Validate unique mobile number
        existing_mobile = await self.repository.get_by_mobile(dto.mobile_number)
        if existing_mobile:
            raise PartyAlreadyExistsException(f"Mobile number '{dto.mobile_number}' is already registered.")

        # Validate unique GST number if provided
        if dto.gst_number:
            existing_gst = await self.repository.get_by_gst(dto.gst_number)
            if existing_gst:
                raise PartyAlreadyExistsException(f"GST number '{dto.gst_number}' is already registered.")

        # Validate unique PAN number if provided
        if dto.pan_number:
            existing_pan = await self.repository.get_by_pan(dto.pan_number)
            if existing_pan:
                raise PartyAlreadyExistsException(f"PAN number '{dto.pan_number}' is already registered.")

        # Construct domain model
        party = Party(
            name=dto.name,
            party_type=dto.party_type,
            mobile_number=dto.mobile_number,
            alternate_mobile=dto.alternate_mobile,
            email=dto.email,
            gst_number=dto.gst_number,
            pan_number=dto.pan_number,
            address=dto.address,
            city=dto.city,
            state=dto.state,
            pincode=dto.pincode,
            contact_person=dto.contact_person,
            opening_balance=dto.opening_balance,
            credit_limit=dto.credit_limit,
            remarks=dto.remarks,
            created_by=current_user_id,
            updated_by=current_user_id,
            is_active=True,
        )

        await self.repository.create(party)
        await self.session.commit()
        return party

    async def get_party_by_id(self, party_id: uuid.UUID) -> Party:
        """
        Loads a single active party by ID.
        Raises PartyNotFoundException if not found.
        """
        party = await self.repository.get_by_id(party_id)
        if not party:
            raise PartyNotFoundException(party_id)
        return party

    async def get_all_parties(self) -> Sequence[Party]:
        """
        Returns all active parties.
        """
        return await self.repository.get_all()

    async def update_party(self, party_id: uuid.UUID, dto: PartyUpdate, current_user_id: uuid.UUID) -> Party:
        """
        Updates an existing party profile.
        Validates unique constraints on changed values.
        Raises PartyNotFoundException or PartyAlreadyExistsException.
        """
        party = await self.repository.get_by_id(party_id)
        if not party:
            raise PartyNotFoundException(party_id)

        # Validation on updated mobile number
        if dto.mobile_number is not None and dto.mobile_number != party.mobile_number:
            existing = await self.repository.get_by_mobile(dto.mobile_number)
            if existing:
                raise PartyAlreadyExistsException(f"Mobile number '{dto.mobile_number}' is already registered.")
            party.mobile_number = dto.mobile_number

        # Validation on updated GST number
        if dto.gst_number is not None and dto.gst_number != party.gst_number:
            existing = await self.repository.get_by_gst(dto.gst_number)
            if existing:
                raise PartyAlreadyExistsException(f"GST number '{dto.gst_number}' is already registered.")
            party.gst_number = dto.gst_number

        # Validation on updated PAN number
        if dto.pan_number is not None and dto.pan_number != party.pan_number:
            existing = await self.repository.get_by_pan(dto.pan_number)
            if existing:
                raise PartyAlreadyExistsException(f"PAN number '{dto.pan_number}' is already registered.")
            party.pan_number = dto.pan_number

        # Update remaining attributes if provided
        if dto.name is not None:
            party.name = dto.name
        if dto.party_type is not None:
            party.party_type = dto.party_type
        if dto.alternate_mobile is not None:
            party.alternate_mobile = dto.alternate_mobile
        if dto.email is not None:
            party.email = dto.email
        if dto.address is not None:
            party.address = dto.address
        if dto.city is not None:
            party.city = dto.city
        if dto.state is not None:
            party.state = dto.state
        if dto.pincode is not None:
            party.pincode = dto.pincode
        if dto.contact_person is not None:
            party.contact_person = dto.contact_person
        if dto.opening_balance is not None:
            party.opening_balance = dto.opening_balance
        if dto.credit_limit is not None:
            party.credit_limit = dto.credit_limit
        if dto.remarks is not None:
            party.remarks = dto.remarks
        if dto.is_active is not None:
            party.is_active = dto.is_active

        # Audit stamping
        party.updated_by = current_user_id
        party.updated_at = datetime.now(timezone.utc)

        await self.repository.update(party)
        await self.session.commit()
        return party

    async def delete_party(self, party_id: uuid.UUID, current_user_id: uuid.UUID) -> bool:
        """
        Soft-deletes a party.
        Raises PartyNotFoundException or PartyHasActiveTripsException.
        """
        party = await self.repository.get_by_id(party_id)
        if not party:
            raise PartyNotFoundException(party_id)

        # Integrity check: verify active trips constraint
        has_trips = await self.repository.has_active_trips(party_id)
        if has_trips:
            raise PartyHasActiveTripsException(party_id)

        # Stamp audit details before marking as soft-deleted
        party.updated_by = current_user_id
        party.updated_at = datetime.now(timezone.utc)
        party.is_active = False

        await self.repository.delete(party_id, soft=True)
        await self.session.commit()
        return True

    async def paginate_parties(
        self,
        page: int,
        size: int,
        search_query: str | None = None,
        party_type_filter: str | None = None,
        status_filter: str | None = None,
        city_filter: str | None = None,
        state_filter: str | None = None,
        created_date_start: str | None = None,
        created_date_end: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[Sequence[Party], int]:
        """
        Fetches a paginated page of parties matching search, sorting, and filter conditions.
        """
        return await self.repository.get_parties(
            page=page,
            size=size,
            search_query=search_query,
            party_type_filter=party_type_filter,
            status_filter=status_filter,
            city_filter=city_filter,
            state_filter=state_filter,
            created_date_start=created_date_start,
            created_date_end=created_date_end,
            sort_by=sort_by,
            order=order,
            include_deleted=include_deleted,
        )
