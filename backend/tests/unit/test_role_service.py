import uuid
import pytest
from unittest.mock import AsyncMock, patch

from app.application.services.role_service import RoleService
from app.domain.entities.role import Role
from app.domain.entities.permission import Permission
from app.application.dtos.roles import RoleCreate, RoleUpdate
from app.domain.exceptions.base import ResourceNotFoundException

@pytest.fixture
def mock_role_repository():
    return AsyncMock()

@pytest.fixture
def mock_permission_repository():
    return AsyncMock()

@pytest.fixture
def role_service(mock_role_repository, mock_permission_repository):
    return RoleService(mock_role_repository, mock_permission_repository)

@pytest.mark.asyncio
async def test_get_role_by_id_success(role_service, mock_role_repository):
    role_id = uuid.uuid4()
    mock_role = Role(id=role_id, name="Admin")
    mock_role_repository.get_by_id.return_value = mock_role
    
    role = await role_service.get_role_by_id(role_id)
    assert role == mock_role
    mock_role_repository.get_by_id.assert_called_once_with(role_id)

@pytest.mark.asyncio
async def test_get_role_by_id_not_found(role_service, mock_role_repository):
    mock_role_repository.get_by_id.return_value = None
    with pytest.raises(ResourceNotFoundException):
        await role_service.get_role_by_id(uuid.uuid4())

@pytest.mark.asyncio
async def test_create_role(role_service, mock_role_repository, mock_permission_repository):
    perm_id = uuid.uuid4()
    dto = RoleCreate(name="Manager", description="Manage things", permission_ids=[perm_id])
    
    mock_permission = Permission(id=perm_id, name="manage")
    mock_permission_repository.get_by_ids.return_value = [mock_permission]
    
    mock_role = Role(name=dto.name, description=dto.description)
    mock_role_repository.create.return_value = mock_role
    
    role = await role_service.create_role(dto)
    
    mock_permission_repository.get_by_ids.assert_called_once_with([perm_id])
    mock_role_repository.create.assert_called_once()
    assert role.name == "Manager"

@pytest.mark.asyncio
@patch("app.application.services.role_service.PermissionCacheService")
async def test_update_role(mock_cache, role_service, mock_role_repository, mock_permission_repository):
    role_id = uuid.uuid4()
    perm_id = uuid.uuid4()
    
    mock_role = Role(id=role_id, name="Old Name")
    mock_role_repository.get_by_id.return_value = mock_role
    
    mock_permission = Permission(id=perm_id, name="manage")
    mock_permission_repository.get_by_ids.return_value = [mock_permission]
    mock_role_repository.update.return_value = mock_role
    
    dto = RoleUpdate(name="New Name", permission_ids=[perm_id])
    
    updated_role = await role_service.update_role(role_id, dto)
    
    mock_role_repository.update.assert_called_once()
    assert updated_role.name == "New Name"
    assert updated_role.permissions == [mock_permission]
    mock_cache.invalidate_all_permissions.assert_called_once()

@pytest.mark.asyncio
@patch("app.application.services.role_service.PermissionCacheService")
async def test_delete_role(mock_cache, role_service, mock_role_repository):
    role_id = uuid.uuid4()
    mock_role = Role(id=role_id, name="Admin")
    mock_role_repository.get_by_id.return_value = mock_role
    
    await role_service.delete_role(role_id)
    
    mock_role_repository.delete.assert_called_once_with(mock_role, deleted_by=None)
    mock_cache.invalidate_all_permissions.assert_called_once()
