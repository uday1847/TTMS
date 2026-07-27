from sqlalchemy import select
from app.domain.entities.role_permission import RolePermission
from app.infrastructure.repositories.role_repository import SQLAlchemyRoleRepository
from app.infrastructure.repositories.permission_repository import SQLAlchemyPermissionRepository
from app.infrastructure.seed.base_seed import BaseSeed
from app.infrastructure.seed.constants import PERMISSION_DEFINITIONS, SYSTEM_USER_ID


class RolePermissionSeed(BaseSeed):
    """
    Seeds mappings between roles and permissions (assigns all default permissions to Super Admin).
    Queries the target role and permissions dynamically.
    """
    async def run(self) -> None:
        session = self.context.session
        role_repo = SQLAlchemyRoleRepository(session)
        perm_repo = SQLAlchemyPermissionRepository(session)
        
        # Look up roles dynamically
        roles_to_seed = ["Super Admin", "Admin"]
        roles = []
        for role_name in roles_to_seed:
            role = await role_repo.get_by_name(role_name)
            if role:
                roles.append(role)
            else:
                self.logger.warning(f"[Seed] Role Permissions     SKIP ({role_name} role not found)")
                
        if not roles:
            return

        created_count = 0
        skipped_count = 0

        for definition in PERMISSION_DEFINITIONS:
            # Look up permission dynamically by code
            perm = await perm_repo.get_by_name(definition["code"])
            if not perm:
                self.logger.warning(f"[Seed] Role Permissions     SKIP (Permission {definition['code']} not found)")
                continue
            
            for role in roles:
                # Exclude system permissions for regular Admin
                if role.name == "Admin" and (definition["code"].startswith("roles:") or definition["code"].startswith("permissions:")):
                    continue

                # Idempotency check: check if the link already exists
                stmt = select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == perm.id
                )
                result = await session.execute(stmt)
                existing_mapping = result.scalar_one_or_none()
    
                if existing_mapping:
                    skipped_count += 1
                    continue
    
                # Create new junction mapping
                mapping = RolePermission(
                    role_id=role.id,
                    permission_id=perm.id,
                    created_by=SYSTEM_USER_ID
                )
                session.add(mapping)
                created_count += 1

        # We must flush to apply the junction records so the session tracks them
        await session.flush()

        if created_count > 0:
            self.logger.info(f"[Seed] Role Permissions     OK (mapped: {created_count}, skipped: {skipped_count})")
        else:
            self.logger.info(f"[Seed] Role Permissions     SKIP (all {skipped_count} mappings exist)")
