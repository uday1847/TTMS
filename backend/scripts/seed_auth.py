import asyncio
import logging
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add current workspace to path to allow imports when running script directly
sys.path.append(".")

from app.infrastructure.database.session import AsyncSessionLocal
from app.core.security import hash_password
from app.domain.entities.permission import Permission
from app.domain.entities.role import Role
from app.domain.entities.user import User

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed")

# Core system permissions list
PERMISSIONS = [
    # User permissions
    ("users:read", "Ability to list and retrieve user details"),
    ("users:create", "Ability to register new users"),
    ("users:update", "Ability to update existing user profiles"),
    ("users:delete", "Ability to soft-delete user accounts"),
    ("users:role_assign", "Ability to assign or remove roles from users"),
    
    # Role permissions
    ("roles:read", "Ability to list roles"),
    ("roles:create", "Ability to define new roles"),
    ("roles:delete", "Ability to delete roles"),
    ("roles:permission_assign", "Ability to bind permissions to roles"),
    
    # Permission permissions
    ("permissions:read", "Ability to view defined permissions catalog"),
    
    # Fleet operational permissions (for master validation consistency)
    ("drivers:read", "Ability to list drivers"),
    ("drivers:create", "Ability to create drivers"),
    ("drivers:update", "Ability to edit drivers"),
    ("drivers:delete", "Ability to delete drivers"),
    
    ("trips:read", "Ability to list trips"),
    ("trips:create", "Ability to create trips"),
    ("trips:update", "Ability to edit trips"),
    ("trips:delete", "Ability to delete trips"),
]


async def seed_data() -> None:
    """
    Main seeding routine executing in a single async transaction.
    """
    logger.info("Starting database seeding...")
    
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # 1. Seed/Fetch Permissions
            permission_entities: dict[str, Permission] = {}
            for code, desc in PERMISSIONS:
                # Check if permission code exists
                stmt = select(Permission).where(Permission.code == code)
                result = await session.execute(stmt)
                perm_obj = result.scalar_one_or_none()
                
                if not perm_obj:
                    perm_obj = Permission(code=code, description=desc, is_active=True)
                    session.add(perm_obj)
                    logger.info(f"Seeding Permission: {code}")
                
                permission_entities[code] = perm_obj

            # 2. Seed/Fetch Roles
            # Admin Role
            stmt_admin_role = select(Role).where(Role.name == "admin")
            res_admin_role = await session.execute(stmt_admin_role)
            admin_role = res_admin_role.scalar_one_or_none()

            if not admin_role:
                admin_role = Role(
                    name="admin",
                    display_name="System Administrator",
                    description="Full administrative access to the system.",
                    is_active=True,
                )
                session.add(admin_role)
                logger.info("Seeding Role: admin")

            # Operator Role
            stmt_op_role = select(Role).where(Role.name == "operator")
            res_op_role = await session.execute(stmt_op_role)
            operator_role = res_op_role.scalar_one_or_none()

            if not operator_role:
                operator_role = Role(
                    name="operator",
                    display_name="System Operator",
                    description="Standard operational access to manage trips and view drivers.",
                    is_active=True,
                )
                session.add(operator_role)
                logger.info("Seeding Role: operator")

            # 3. Associate Permissions to Roles
            # Admin gets all permissions
            for perm in permission_entities.values():
                if perm not in admin_role.permissions:
                    admin_role.permissions.append(perm)

            # Operator gets subset (read privileges + operational trips create/read)
            op_permissions = ["users:read", "roles:read", "permissions:read", "drivers:read", "trips:read", "trips:create"]
            for code in op_permissions:
                perm_entity = permission_entities.get(code)
                if perm_entity and perm_entity not in operator_role.permissions:
                    operator_role.permissions.append(perm_entity)

            # 4. Seed Default Administrator User
            stmt_admin_user = select(User).where(User.email == "admin@ttms.com")
            res_admin_user = await session.execute(stmt_admin_user)
            admin_user = res_admin_user.scalar_one_or_none()

            if not admin_user:
                admin_user = User(
                    email="admin@ttms.com",
                    username="admin",
                    password_hash=hash_password("AdminPassword123!"),
                    first_name="System",
                    last_name="Administrator",
                    is_active=True,
                )
                session.add(admin_user)
                logger.info("Seeding User: admin@ttms.com (password: AdminPassword123!)")

            # Bind Admin role to Admin user
            if admin_role not in admin_user.roles:
                admin_user.roles.append(admin_role)

            # Set self-referential audit stamps
            await session.flush()  # Populates user and role IDs
            admin_user.created_by = admin_user.id
            admin_user.updated_by = admin_user.id
            
            admin_role.created_by = admin_user.id
            admin_role.updated_by = admin_user.id
            
            operator_role.created_by = admin_user.id
            operator_role.updated_by = admin_user.id

            for perm in permission_entities.values():
                if perm.created_by is None:
                    perm.created_by = admin_user.id
                    perm.updated_by = admin_user.id

    logger.info("Database seeding successfully completed.")


if __name__ == "__main__":
    asyncio.run(seed_data())
