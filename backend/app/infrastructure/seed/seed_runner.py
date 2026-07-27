import asyncio
import logging
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.settings import settings
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.seed.base_seed import SeedContext
from app.infrastructure.seed.registry import SEEDS
from sqlalchemy import text

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

    # Validation and Summary
    logger.info("Running post-seed validation...")
    
    # Check permissions vs mappings
    result = await session.execute(text("""
        SELECT p.name 
        FROM role_permissions rp
        JOIN permissions p ON rp.permission_id = p.id
    """))
    mapped_perms = [r[0] for r in result.fetchall()]
    
    # Check if there are permissions in mappings that don't exist (this is theoretically impossible due to FK, but we'll check it anyway)
    # The more relevant check: verify all permissions in constants were mapped to Super Admin
    from app.infrastructure.seed.constants import PERMISSION_DEFINITIONS
    expected_perms = set(p["code"] for p in PERMISSION_DEFINITIONS)
    
    if not expected_perms.issubset(set(mapped_perms)):
        missing = expected_perms - set(mapped_perms)
        logger.error(f"Post-seed validation failed: Missing permissions in mappings: {missing}")
        raise ValueError(f"Missing mapped permissions: {missing}")
        
    roles_count = (await session.execute(text("SELECT COUNT(*) FROM roles"))).scalar()
    perms_count = (await session.execute(text("SELECT COUNT(*) FROM permissions"))).scalar()
    mappings_count = (await session.execute(text("SELECT COUNT(*) FROM role_permissions"))).scalar()
    users_count = (await session.execute(text("SELECT COUNT(*) FROM users"))).scalar()
    
    logger.info(f"--- SEED SUMMARY ---")
    logger.info(f"Roles created/verified: {roles_count}")
    logger.info(f"Permissions created/verified: {perms_count}")
    logger.info(f"Mappings created/verified: {mappings_count}")
    logger.info(f"Users created/verified: {users_count}")
    logger.info(f"--------------------")



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
