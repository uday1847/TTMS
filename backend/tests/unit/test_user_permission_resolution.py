import pytest
import uuid
from app.application.services.user_service import UserService
from app.domain.entities.user import User
from app.domain.entities.role import Role
from app.domain.entities.permission import Permission
from app.domain.entities.user_permission import UserPermission

from unittest.mock import MagicMock

@pytest.fixture
def mock_user_service():
    service = UserService(
        user_repository=MagicMock(),
        role_repository=MagicMock()
    )
    return service

def test_calculate_effective_permissions_no_roles_no_overrides(mock_user_service):
    user = User(id=uuid.uuid4(), email="test@example.com")
    user.roles = []
    user.direct_permissions = []
    
    perms = mock_user_service._calculate_effective_permissions(user)
    assert perms == []

def test_calculate_effective_permissions_roles_only(mock_user_service):
    user = User(id=uuid.uuid4(), email="test@example.com")
    
    perm1 = Permission(id=uuid.uuid4(), name="users:read", module="Users")
    perm2 = Permission(id=uuid.uuid4(), name="users:write", module="Users")
    role = Role(id=uuid.uuid4(), name="Admin", permissions=[perm1, perm2])
    
    user.roles = [role]
    user.direct_permissions = []
    
    perms = mock_user_service._calculate_effective_permissions(user)
    assert sorted(perms) == sorted(["users:read", "users:write"])

def test_calculate_effective_permissions_with_grants(mock_user_service):
    user = User(id=uuid.uuid4(), email="test@example.com")
    
    perm1 = Permission(id=uuid.uuid4(), name="users:read", module="Users")
    role = Role(id=uuid.uuid4(), name="Viewer", permissions=[perm1])
    
    user.roles = [role]
    
    perm2 = Permission(id=uuid.uuid4(), name="users:write", module="Users")
    up = UserPermission(user_id=user.id, permission_id=perm2.id, is_granted=True, permission=perm2)
    user.direct_permissions = [up]
    
    perms = mock_user_service._calculate_effective_permissions(user)
    assert sorted(perms) == sorted(["users:read", "users:write"])

def test_calculate_effective_permissions_with_revokes(mock_user_service):
    user = User(id=uuid.uuid4(), email="test@example.com")
    
    perm1 = Permission(id=uuid.uuid4(), name="users:read", module="Users")
    perm2 = Permission(id=uuid.uuid4(), name="users:write", module="Users")
    role = Role(id=uuid.uuid4(), name="Admin", permissions=[perm1, perm2])
    
    user.roles = [role]
    
    up = UserPermission(user_id=user.id, permission_id=perm2.id, is_granted=False, permission=perm2)
    user.direct_permissions = [up]
    
    perms = mock_user_service._calculate_effective_permissions(user)
    assert perms == ["users:read"]
