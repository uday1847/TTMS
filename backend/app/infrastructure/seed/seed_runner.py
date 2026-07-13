import asyncio
import logging
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.seed.base_seed import SeedContext
from app.infrastructure.seed.registry import SEEDS

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ttms.seed")


async def run_seeds(session: AsyncSession) -> None:
    """
    Instantiates and executes each seed module in the registered sequence.
    """
    context = SeedContext(session=session, settings=settings)
    for seed_class in SEEDS:
        seed_instance = seed_class(context)
        await seed_instance.run()


async def main() -> None:
    """
    Main entry point for executing the database seeding script.
    Encapsulates all seeds within a single transaction boundaries.
    """
    logger.info("Initializing database seeding runner...")
    
    try:
        async with AsyncSessionLocal() as session:
            # Execute within a transaction block.
            # SQLAlchemy will automatically commit on success and rollback on exception.
            async with session.begin():
                await run_seeds(session)
                
        logger.info("Database seeding successfully completed.")
    except Exception as e:
        logger.error(f"Database seeding aborted due to critical error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
