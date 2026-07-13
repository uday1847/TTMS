import asyncio
import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import AsyncSessionLocal, engine
from app.domain.entities.user import User


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    """
    Fixture providing an active AsyncSession for database integration testing.
    Disposes of the global pool and cleans up any leftover integration test records
    before yielding the session to ensure a clean, self-healing setup.
    """
    # Force pool disposal so connections bind to the current active event loop
    await engine.dispose()
    
    async with AsyncSessionLocal() as session:
        # Pre-test self-healing database cleanup
        async with session.begin():
            await session.execute(
                delete(User).where(User.email.like("integration%"))
            )
            
        yield session
        
    # Dispose pool after test to release connections cleanly
    await engine.dispose()
