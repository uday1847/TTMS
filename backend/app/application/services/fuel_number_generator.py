from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.domain.entities.fuel_transaction import FuelTransaction


class FuelNumberGenerator:
    """
    Generates sequential fuel transaction numbers for the system.
    Format: FUEL-{YYYYMMDD}-{SEQ}
    Example: FUEL-20231015-001
    """

    @staticmethod
    async def generate(session: AsyncSession, date_str: str) -> str:
        """
        Generate the next sequential fuel transaction number for the given date.
        """
        prefix = f"FUEL-{date_str}"

        # Find the maximum sequence number for the current prefix
        stmt = (
            select(func.max(FuelTransaction.fuel_number))
            .where(FuelTransaction.fuel_number.like(f"{prefix}-%"))
        )
        
        result = await session.execute(stmt)
        max_number = result.scalar_one_or_none()

        if max_number:
            # Extract the sequence part and increment
            try:
                current_seq = int(max_number.split("-")[-1])
                next_seq = current_seq + 1
            except ValueError:
                next_seq = 1
        else:
            next_seq = 1

        return f"{prefix}-{next_seq:03d}"
