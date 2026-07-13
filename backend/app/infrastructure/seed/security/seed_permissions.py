from app.domain.entities.permission import Permission
from app.infrastructure.repositories.permission_repository import SQLAlchemyPermissionRepository
from app.infrastructure.seed.base_seed import BaseSeed
from app.infrastructure.seed.constants import PERMISSION_DEFINITIONS, SYSTEM_USER_ID


class PermissionSeed(BaseSeed):
    """
    Seeds default system permissions using fixed UUIDs and codes.
    """
    async def run(self) -> None:
        perm_repo = SQLAlchemyPermissionRepository(self.context.session)
        created_count = 0
        skipped_count = 0

        for definition in PERMISSION_DEFINITIONS:
            # Check if permission already exists by ID or by code
            existing_perm = await perm_repo.get_by_id(definition["id"])
            if not existing_perm:
                existing_perm = await perm_repo.get_by_code(definition["code"])

            if existing_perm:
                skipped_count += 1
                continue

            # Create new permission
            new_perm = Permission(
                id=definition["id"],
                code=definition["code"],
                description=definition["description"],
                is_active=True,
                created_by=SYSTEM_USER_ID,
                updated_by=SYSTEM_USER_ID,
            )
            await perm_repo.create(new_perm)
            created_count += 1

        if created_count > 0:
            self.logger.info(f"[Seed] Permissions           OK (created: {created_count}, skipped: {skipped_count})")
        else:
            self.logger.info(f"[Seed] Permissions           SKIP (all {skipped_count} permissions exist)")
