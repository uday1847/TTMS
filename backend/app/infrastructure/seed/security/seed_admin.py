from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.seed.base_seed import BaseSeed
from app.infrastructure.seed.constants import SUPER_ADMIN_USER_ID, SYSTEM_USER_ID
from app.core.security import hash_password


class AdminSeed(BaseSeed):
    """
    Seeds the Super Admin user account using the default password set in configuration.
    """
    async def run(self) -> None:
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

        # Hash default admin password from settings config
        admin_password_hash = hash_password(self.context.settings.DEFAULT_ADMIN_PASSWORD)

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
