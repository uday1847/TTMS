import os
from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.seed.base_seed import BaseSeed
from app.infrastructure.seed.constants import SUPER_ADMIN_USER_ID, SYSTEM_USER_ID
from app.core.security import hash_password
from app.core.settings import settings


class AdminSeed(BaseSeed):
    """
    Seeds the Super Admin user account using the password from ADMIN_PASSWORD environment variable.
    """
    async def run(self) -> None:
        admin_email = settings.FIRST_SUPERUSER_EMAIL
        admin_username = settings.FIRST_SUPERUSER_USERNAME
        admin_password = settings.FIRST_SUPERUSER_PASSWORD

        if not admin_password:
            self.logger.error("[Seed] Super Admin          SKIP (FIRST_SUPERUSER_PASSWORD missing)")
            return

        if admin_password == "Admin@123":
            self.logger.warning("[Seed] Super Admin          WARNING (Using default superuser password. Change it before production deployment.)")

        user_repo = SQLAlchemyUserRepository(self.context.session)

        # Idempotency check: verify by fixed SUPER_ADMIN_USER_ID, username, and email
        existing_admin = await user_repo.get_by_id(SUPER_ADMIN_USER_ID)
        if not existing_admin:
            existing_admin = await user_repo.get_by_username(admin_username)
        if not existing_admin:
            existing_admin = await user_repo.get_by_email(admin_email)
            
        if existing_admin:
            self.logger.info("[Seed] Super Admin          SKIP (exists)")
            return

        # Hash admin password from environment variable
        admin_password_hash = hash_password(admin_password)

        admin_user = User(
            id=SUPER_ADMIN_USER_ID,
            username=admin_username,
            email=admin_email,
            password_hash=admin_password_hash,
            first_name="Super",
            last_name="Administrator",
            is_active=True,
            created_by=SYSTEM_USER_ID,
            updated_by=SYSTEM_USER_ID,
        )

        await user_repo.create(admin_user)
        self.logger.info("[Seed] Super Admin          OK (created)")
