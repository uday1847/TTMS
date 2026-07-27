import uuid
from sqlalchemy import select
from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.seed.base_seed import BaseSeed
from app.infrastructure.seed.constants import SYSTEM_USER_ID
from app.core.security import hash_password


class SystemUserSeed(BaseSeed):
    """
    Seeds the internal System User account used for background processes,
    automated audits, and tracking database record creation/modification audits.
    """
    async def run(self) -> None:
        user_repo = SQLAlchemyUserRepository(self.context.session)
        
        # Idempotency check: verify by fixed SYSTEM_USER_ID, username, and email
        system_user = await user_repo.get_by_id(SYSTEM_USER_ID)
        if not system_user:
            system_user = await user_repo.get_by_username("system")
        if not system_user:
            system_user = await user_repo.get_by_email("system@ttms.com")
            
        if system_user:
            self.logger.info("[Seed] System User          SKIP (exists)")
            return

        # Create system user
        # Secure password hash since the user cannot authenticate
        dummy_password_hash = hash_password("SystemAccountNonInteractiveSecretPassword!#%7")
        
        system_user = User(
            id=SYSTEM_USER_ID,
            username="system",
            email="system@ttms.com",
            password_hash=dummy_password_hash,
            first_name="System",
            last_name="User",
            is_active=True,
            created_by=None,
            updated_by=None,
        )
        
        await user_repo.create(system_user)
        self.logger.info("[Seed] System User          OK (created)")
