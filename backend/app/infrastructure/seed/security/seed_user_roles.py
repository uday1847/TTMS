from sqlalchemy import select
from app.domain.entities.user_role import UserRole
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.repositories.role_repository import SQLAlchemyRoleRepository
from app.infrastructure.seed.base_seed import BaseSeed
from app.infrastructure.seed.constants import SYSTEM_USER_ID


class UserRoleSeed(BaseSeed):
    """
    Seeds user-role associations (assigns the Super Admin role to the Super Admin user).
    Queries target user and role dynamically to ensure correct FK references.
    """
    async def run(self) -> None:
        session = self.context.session
        user_repo = SQLAlchemyUserRepository(session)
        role_repo = SQLAlchemyRoleRepository(session)

        # Retrieve user and role dynamically by unique keys
        user = await user_repo.get_by_username("admin")
        if not user:
            user = await user_repo.get_by_email("admin@ttms.local")
            
        role = await role_repo.get_by_name("Super Admin")

        if not user or not role:
            self.logger.warning("[Seed] User Roles          SKIP (User or Role not found)")
            return

        # Idempotency check: check if the user is already assigned the role
        stmt = select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id
        )
        result = await session.execute(stmt)
        existing_mapping = result.scalar_one_or_none()

        if existing_mapping:
            self.logger.info("[Seed] User Roles          SKIP (exists)")
            return

        # Assign role to user
        mapping = UserRole(
            user_id=user.id,
            role_id=role.id,
            created_by=SYSTEM_USER_ID
        )
        session.add(mapping)
        await session.flush()

        self.logger.info("[Seed] User Roles          OK (mapped)")
