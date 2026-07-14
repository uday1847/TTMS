import uuid
from decimal import Decimal
from typing import Any, Tuple

from app.application.dtos.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceStatusUpdate
from app.application.services.maintenance_number_generator import MaintenanceNumberGenerator
from app.domain.entities.maintenance import Maintenance
from app.domain.entities.maintenance_history import MaintenanceHistory
from app.domain.enums.maintenance_status import MaintenanceStatus
from app.domain.enums.tractor_status import TractorStatus
from app.domain.exceptions.maintenance import (
    MaintenanceNotFoundException,
    MaintenanceAlreadyScheduledException,
    MaintenanceStatusException,
    MaintenanceValidationException,
    MaintenanceDeleteException,
)
from app.domain.exceptions.tractor import TractorNotFoundException
from app.domain.exceptions.trip import InactiveTractorException
from app.domain.repositories.maintenance_repository import MaintenanceRepository
from app.domain.repositories.tractor_repository import TractorRepository
from app.infrastructure.database.session import AsyncSessionLocal


class MaintenanceService:
    def __init__(self, maintenance_repo: MaintenanceRepository, tractor_repo: TractorRepository):
        self.maintenance_repo = maintenance_repo
        self.tractor_repo = tractor_repo

    async def _calculate_total_cost(self, parts_cost: Decimal, labor_cost: Decimal, other_cost: Decimal) -> Decimal:
        return (parts_cost or Decimal("0.00")) + (labor_cost or Decimal("0.00")) + (other_cost or Decimal("0.00"))

    async def create_maintenance(self, data: MaintenanceCreate, user_id: uuid.UUID) -> Maintenance:
        tractor = await self.tractor_repo.get_by_id(data.tractor_id)
        if not tractor:
            raise TractorNotFoundException()
        if not tractor.is_active:
            raise InactiveTractorException()
            
        if data.current_odometer < tractor.current_odometer:
            raise MaintenanceValidationException("Maintenance odometer cannot be less than tractor's current odometer.")

        active_maintenance = await self.maintenance_repo.get_active_for_tractor(data.tractor_id)
        if active_maintenance:
            raise MaintenanceAlreadyScheduledException()

        total_cost = await self._calculate_total_cost(data.parts_cost, data.labor_cost, data.other_cost)

        async with AsyncSessionLocal() as session:
            maintenance_number = await MaintenanceNumberGenerator.generate(session)

        maintenance = Maintenance(
            maintenance_number=maintenance_number,
            tractor_id=data.tractor_id,
            maintenance_type=data.maintenance_type,
            priority=data.priority,
            status=MaintenanceStatus.SCHEDULED,
            vendor_name=data.vendor_name,
            vendor_mobile=data.vendor_mobile,
            service_center=data.service_center,
            invoice_number=data.invoice_number,
            scheduled_date=data.scheduled_date,
            start_date=data.start_date,
            completion_date=data.completion_date,
            next_service_date=data.next_service_date,
            current_odometer=data.current_odometer,
            next_service_odometer=data.next_service_odometer,
            parts_cost=data.parts_cost,
            labor_cost=data.labor_cost,
            other_cost=data.other_cost,
            total_cost=total_cost,
            remarks=data.remarks,
            attachment=data.attachment,
            created_by=user_id,
        )

        history = MaintenanceHistory(
            new_status=MaintenanceStatus.SCHEDULED,
            new_vendor_name=data.vendor_name,
            new_total_cost=total_cost,
            new_odometer=data.current_odometer,
            remarks="Maintenance created",
            changed_by=user_id,
        )
        maintenance.histories.append(history)

        return await self.maintenance_repo.save(maintenance)

    async def update_maintenance(self, maintenance_id: uuid.UUID, data: MaintenanceUpdate, user_id: uuid.UUID) -> Maintenance:
        maintenance = await self.maintenance_repo.get_by_id(maintenance_id)
        if not maintenance:
            raise MaintenanceNotFoundException()
            
        if maintenance.status in [MaintenanceStatus.COMPLETED, MaintenanceStatus.CANCELLED]:
            raise MaintenanceValidationException("Cannot edit a COMPLETED or CANCELLED maintenance record")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return maintenance

        history = MaintenanceHistory(changed_by=user_id, remarks="Maintenance details updated")
        
        if "vendor_name" in update_data:
            history.old_vendor_name = maintenance.vendor_name
            history.new_vendor_name = update_data["vendor_name"]
            
        if "current_odometer" in update_data:
            history.old_odometer = maintenance.current_odometer
            history.new_odometer = update_data["current_odometer"]

        for key, value in update_data.items():
            setattr(maintenance, key, value)

        new_total_cost = await self._calculate_total_cost(maintenance.parts_cost, maintenance.labor_cost, maintenance.other_cost)
        if maintenance.total_cost != new_total_cost:
            history.old_total_cost = maintenance.total_cost
            history.new_total_cost = new_total_cost
            maintenance.total_cost = new_total_cost

        maintenance.updated_by = user_id
        
        if any([history.old_vendor_name, history.new_vendor_name, history.old_total_cost, history.new_total_cost, history.old_odometer, history.new_odometer]):
            maintenance.histories.append(history)

        return await self.maintenance_repo.save(maintenance)

    async def update_status(self, maintenance_id: uuid.UUID, data: MaintenanceStatusUpdate, user_id: uuid.UUID) -> Maintenance:
        maintenance = await self.maintenance_repo.get_by_id(maintenance_id)
        if not maintenance:
            raise MaintenanceNotFoundException()

        current_status = maintenance.status
        new_status = data.status

        if current_status == new_status:
            return maintenance

        valid_transitions = {
            MaintenanceStatus.SCHEDULED: [MaintenanceStatus.IN_PROGRESS, MaintenanceStatus.CANCELLED],
            MaintenanceStatus.IN_PROGRESS: [MaintenanceStatus.COMPLETED],
            MaintenanceStatus.COMPLETED: [],
            MaintenanceStatus.CANCELLED: [],
        }

        if new_status not in valid_transitions[current_status]:
            raise MaintenanceStatusException(f"Cannot transition from {current_status} to {new_status}")

        tractor = await self.tractor_repo.get_by_id(maintenance.tractor_id)
        
        if new_status == MaintenanceStatus.IN_PROGRESS:
            if tractor.status == TractorStatus.IN_MAINTENANCE:
                # Edge case safeguard
                pass
            tractor.status = TractorStatus.IN_MAINTENANCE

        elif new_status == MaintenanceStatus.COMPLETED:
            tractor.status = TractorStatus.ACTIVE
            if maintenance.current_odometer > tractor.current_odometer:
                tractor.current_odometer = maintenance.current_odometer

        elif new_status == MaintenanceStatus.CANCELLED:
            tractor.status = TractorStatus.ACTIVE

        history = MaintenanceHistory(
            old_status=current_status,
            new_status=new_status,
            remarks=data.remarks or f"Status changed from {current_status} to {new_status}",
            changed_by=user_id,
        )

        maintenance.status = new_status
        maintenance.updated_by = user_id
        maintenance.histories.append(history)

        # Let the repo save cascade updates to tractor and history
        return await self.maintenance_repo.save(maintenance)

    async def get_maintenance(self, maintenance_id: uuid.UUID) -> Maintenance:
        maintenance = await self.maintenance_repo.get_by_id(maintenance_id)
        if not maintenance:
            raise MaintenanceNotFoundException()
        return maintenance

    async def search_maintenances(self, filters: dict[str, Any], page: int, size: int) -> Tuple[list[Maintenance], int]:
        return await self.maintenance_repo.search(filters, page, size)

    async def get_dashboard(self) -> dict[str, Any]:
        return await self.maintenance_repo.get_dashboard_stats()

    async def get_upcoming_services(self) -> list[Maintenance]:
        return await self.maintenance_repo.get_upcoming_services()

    async def get_overdue_services(self) -> list[Maintenance]:
        return await self.maintenance_repo.get_overdue_services()

    async def delete_maintenance(self, maintenance_id: uuid.UUID, user_id: uuid.UUID) -> None:
        maintenance = await self.maintenance_repo.get_by_id(maintenance_id)
        if not maintenance:
            raise MaintenanceNotFoundException()

        if maintenance.status != MaintenanceStatus.SCHEDULED:
            raise MaintenanceDeleteException()

        await self.maintenance_repo.soft_delete(maintenance_id, user_id)

    async def restore_maintenance(self, maintenance_id: uuid.UUID, user_id: uuid.UUID) -> Maintenance:
        return await self.maintenance_repo.restore(maintenance_id, user_id)
