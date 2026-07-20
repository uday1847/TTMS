import os
from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.seed.base_seed import BaseSeed
from app.infrastructure.seed.constants import SUPER_ADMIN_USER_ID, SYSTEM_USER_ID
from app.core.security import hash_password


class AdminSeed(BaseSeed):
    """
    Seeds the Super Admin user account using the password from ADMIN_PASSWORD environment variable.
    """
    async def run(self) -> None:
        # Require ADMIN_PASSWORD from environment for bootstrap security
        admin_password = os.getenv("ADMIN_PASSWORD")
        if not admin_password:
            self.logger.error("[Seed] Super Admin          SKIP (ADMIN_PASSWORD not set in environment)")
            raise ValueError(
                "ADMIN_PASSWORD environment variable is required for initial admin account creation. "
                "Set ADMIN_PASSWORD before running database seed."
            )
        
        user_repo = SQLAlchemyUserRepository(self.context.session)

        # Idempotency check: verify by fixed SUPER_ADMIN_USER_ID, username, and email
        existing_admin = await user_repo.get_by_id(SUPER_ADMIN_USER_ID)
        if not existing_admin:
            existing_admin = await user_repo.get_by_username("admin")
        if not existing_admin:
            existing_admin = await user_repo.get_by_email("admin@ttms.local")
            
        if existing_admin:
            self.logger.info("[Seed] Super Admin          SKIP (exists)")
            return

        # Hash admin password from environment variable
        admin_password_hash = hash_password(admin_password)

        admin_user = User(
            id=SUPER_ADMIN_USER_ID,
            username="admin",
            email="admin@ttms.local",
            password_hash=admin_password_hash,
            first_name="Super",
            last_name="Administrator",
            is_active=True,
            created_by=SYSTEM_USER_ID,
            updated_by=SYSTEM_USER_ID,
        )

        await user_repo.create(admin_user)
        self.logger.info("[Seed] Super Admin          OK (created)")
