import asyncio
from sqlalchemy import text
from app.infrastructure.database.session import engine

async def drop():
    async with engine.begin() as conn:
        await conn.execute(text("DROP TYPE IF EXISTS maintenance_type_enum CASCADE;"))
        await conn.execute(text("DROP TYPE IF EXISTS maintenance_priority_enum CASCADE;"))
        await conn.execute(text("DROP TYPE IF EXISTS maintenance_status_enum CASCADE;"))
        await conn.execute(text("DROP TYPE IF EXISTS tractor_status_enum CASCADE;"))

asyncio.run(drop())
