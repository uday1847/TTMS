from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import AsyncSessionLocal


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency yielding an async database session for request lifecycles.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
