from datetime import datetime
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.maintenance import Maintenance


class MaintenanceNumberGenerator:
    """
    Generates sequential maintenance tracking numbers in the format MNT-YYYY-XXXXXX.
    Example: MNT-2026-000001
    """

    @staticmethod
    async def generate(session: AsyncSession) -> str:
        current_year = datetime.now().year
        prefix = f"MNT-{current_year}-"

        stmt = (
            select(Maintenance.maintenance_number)
            .where(Maintenance.maintenance_number.like(f"{prefix}%"))
            .order_by(desc(Maintenance.maintenance_number))
            .limit(1)
        )
        
        result = await session.execute(stmt)
        last_number = result.scalar_one_or_none()

        if not last_number:
            next_sequence = 1
        else:
            try:
                # MNT-2026-000001 -> 000001
                sequence_str = last_number.split("-")[-1]
                next_sequence = int(sequence_str) + 1
            except (ValueError, IndexError):
                next_sequence = 1

        return f"{prefix}{next_sequence:06d}"
