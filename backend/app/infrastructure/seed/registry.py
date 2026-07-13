from app.infrastructure.seed.system.seed_system import SystemUserSeed
from app.infrastructure.seed.security.seed_roles import RoleSeed
from app.infrastructure.seed.security.seed_permissions import PermissionSeed
from app.infrastructure.seed.security.seed_role_permissions import RolePermissionSeed
from app.infrastructure.seed.security.seed_admin import AdminSeed
from app.infrastructure.seed.security.seed_user_roles import UserRoleSeed

# Registry of seed operations executed in topological order to respect foreign key constraints.
SEEDS = [
    SystemUserSeed,
    RoleSeed,
    PermissionSeed,
    RolePermissionSeed,
    AdminSeed,
    UserRoleSeed,
]
