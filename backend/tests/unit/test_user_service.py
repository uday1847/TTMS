import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from datetime import datetime
from app.application.services.user_service import UserService
from app.domain.entities.user import User
from app.domain.entities.role import Role
from app.application.dtos.users import UserCreate, UserUpdate
from app.domain.enums.user_status import UserStatus
from app.domain.exceptions.base import ResourceNotFoundException, ValidationException

@pytest.fixture
def mock_user_repository():
    return AsyncMock()

@pytest.fixture
def mock_role_repository():
    return AsyncMock()

@pytest.fixture
def user_service(mock_user_repository, mock_role_repository):
    return UserService(mock_user_repository, mock_role_repository)

@pytest.mark.asyncio
async def test_get_user_by_id_success(user_service, mock_user_repository):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, email="test@example.com")
    mock_user_repository.get_with_roles_and_permissions.return_value = mock_user
    
    user = await user_service.get_user_by_id(user_id)
    assert user == mock_user
    mock_user_repository.get_with_roles_and_permissions.assert_called_once_with(user_id)

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service, mock_user_repository):
    mock_user_repository.get_with_roles_and_permissions.return_value = None
    with pytest.raises(ResourceNotFoundException):
        await user_service.get_user_by_id(uuid.uuid4())

@pytest.mark.asyncio
@patch("app.application.services.user_service.security_settings")
async def test_create_user_success(mock_security, user_service, mock_user_repository, mock_role_repository):
    mock_security.get_password_hash.return_value = "hashed_pass"
    mock_user_repository.get_by_email.return_value = None
    
    role_id = uuid.uuid4()
    mock_role = Role(id=role_id, name="Admin")
    mock_role_repository.get_by_id.return_value = mock_role
    
    dto = UserCreate(
        email="test@example.com",
        username="tester",
        password="Password123!",
        first_name="Test",
        last_name="User",
        phone="1234567890",
        role_ids=[role_id]
    )
    
    mock_created_user = User(email=dto.email)
    mock_user_repository.create.return_value = mock_created_user
    
    user = await user_service.create_user(dto)
    
    mock_user_repository.get_by_email.assert_called_once_with(dto.email)
    mock_security.get_password_hash.assert_called_once_with(dto.password)
    mock_role_repository.get_by_id.assert_called_once_with(role_id)
    mock_user_repository.create.assert_called_once()
    assert user == mock_created_user

@pytest.mark.asyncio
async def test_create_user_duplicate_email(user_service, mock_user_repository):
    mock_user_repository.get_by_email.return_value = User(email="test@example.com")
    
    dto = UserCreate(
        email="test@example.com",
        username="tester",
        password="Password123!",
        first_name="Test",
        last_name="User"
    )
    
    with pytest.raises(ValidationException, match="Email already exists"):
        await user_service.create_user(dto)

@pytest.mark.asyncio
@patch("app.application.services.user_service.PermissionCacheService")
async def test_update_user_with_roles(mock_cache, user_service, mock_user_repository, mock_role_repository):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, email="test@example.com", token_version=1, roles=[])
    mock_user_repository.get_with_roles_and_permissions.return_value = mock_user
    
    role_id = uuid.uuid4()
    mock_role = Role(id=role_id, name="Admin")
    mock_role_repository.get_by_id.return_value = mock_role
    
    mock_user_repository.update.return_value = mock_user
    
    dto = UserUpdate(first_name="NewName", role_ids=[role_id])
    
    updated_user = await user_service.update_user(user_id, dto)
    
    assert updated_user.first_name == "NewName"
    assert updated_user.roles == [mock_role]
    assert updated_user.token_version == 2
    mock_cache.invalidate_user_permissions.assert_called_once_with(str(user_id))
    mock_user_repository.update.assert_called_once_with(mock_user)

@pytest.mark.asyncio
async def test_lock_user(user_service, mock_user_repository):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, email="test@example.com", status=UserStatus.ACTIVE, token_version=1)
    mock_user_repository.get_with_roles_and_permissions.return_value = mock_user
    mock_user_repository.update.return_value = mock_user
    
    user = await user_service.lock_user(user_id)
    
    assert user.status == UserStatus.LOCKED
    assert user.token_version == 2
    mock_user_repository.update.assert_called_once_with(mock_user)

@pytest.mark.asyncio
async def test_unlock_user(user_service, mock_user_repository):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, email="test@example.com", status=UserStatus.LOCKED, failed_login_attempts=5, locked_until=datetime.now())
    mock_user_repository.get_with_roles_and_permissions.return_value = mock_user
    mock_user_repository.update.return_value = mock_user
    
    user = await user_service.unlock_user(user_id)
    
    assert user.status == UserStatus.ACTIVE
    assert user.failed_login_attempts == 0
    assert user.locked_until is None
    mock_user_repository.update.assert_called_once_with(mock_user)

@pytest.mark.asyncio
async def test_delete_user(user_service, mock_user_repository):
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, email="test@example.com", token_version=1)
    mock_user_repository.get_with_roles_and_permissions.return_value = mock_user
    
    await user_service.delete_user(user_id)
    
    assert mock_user.token_version == 2
    mock_user_repository.delete.assert_called_once_with(mock_user, deleted_by=None)
