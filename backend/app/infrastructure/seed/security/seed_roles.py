from app.domain.entities.role import Role
from app.infrastructure.repositories.role_repository import SQLAlchemyRoleRepository
from app.infrastructure.seed.base_seed import BaseSeed
from app.infrastructure.seed.constants import ROLE_DEFINITIONS, SYSTEM_USER_ID


class RoleSeed(BaseSeed):
    """
    Seeds the standard security roles required for system authorization.
    All records are checked against fixed UUIDs and names to avoid duplication.
    """
    async def run(self) -> None:
        role_repo = SQLAlchemyRoleRepository(self.context.session)
        created_count = 0
        skipped_count = 0

        for definition in ROLE_DEFINITIONS:
            # Check if role already exists by ID or by name
            existing_role = await role_repo.get_by_id(definition["id"])
            if not existing_role:
                existing_role = await role_repo.get_by_name(definition["name"])

            if existing_role:
                skipped_count += 1
                continue

            # Create new role
            new_role = Role(
                id=definition["id"],
                name=definition["name"],
                display_name=definition["display_name"],
                description=definition["description"],
                is_active=True,
                created_by=SYSTEM_USER_ID,
                updated_by=SYSTEM_USER_ID,
            )
            await role_repo.create(new_role)
            created_count += 1

        if created_count > 0:
            self.logger.info(f"[Seed] Roles                OK (created: {created_count}, skipped: {skipped_count})")
        else:
            self.logger.info(f"[Seed] Roles                SKIP (all {skipped_count} roles exist)")
