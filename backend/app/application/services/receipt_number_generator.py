from datetime import date
from sqlalchemy import select, String, cast

from app.domain.entities.invoice_payment import InvoicePayment
from app.infrastructure.database.session import AsyncSessionLocal


class ReceiptNumberGenerator:
    """
    Service responsible for generating sequential receipt numbers in the format RCPT-YYYY-XXXXXX
    """
    
    @staticmethod
    async def generate() -> str:
        current_year = date.today().year
        prefix = f"RCPT-{current_year}-"
        
        async with AsyncSessionLocal() as session:
            # Query for the highest receipt number matching the current year's prefix
            stmt = (
                select(InvoicePayment.receipt_number)
                .where(cast(InvoicePayment.receipt_number, String).like(f"{prefix}%"))
                .order_by(InvoicePayment.receipt_number.desc())
                .limit(1)
            )
            
            result = await session.execute(stmt)
            last_receipt = result.scalar_one_or_none()
            
            if not last_receipt:
                next_sequence = 1
            else:
                try:
                    # Extract the sequence part (e.g. RCPT-2026-000001 -> 000001)
                    sequence_str = last_receipt.split("-")[-1]
                    next_sequence = int(sequence_str) + 1
                except (ValueError, IndexError):
                    next_sequence = 1
                    
            return f"{prefix}{next_sequence:06d}"
