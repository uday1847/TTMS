import pytest
import uuid
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.role import Role
from app.domain.entities.permission import Permission
from app.infrastructure.repositories.role_repository import SQLAlchemyRoleRepository

@pytest.mark.asyncio
async def test_sqlalchemy_role_repository_crud(db_session: AsyncSession) -> None:
    role_repo = SQLAlchemyRoleRepository(db_session)
    role_name = f"integration_role_{uuid.uuid4().hex[:8]}"
    
    role = Role(
        name=role_name,
        display_name="Integration Role",
        description="Integration Role",
        is_active=True
    )
    
    await role_repo.create(role)
    await db_session.commit()
        
    assert role.id is not None
    assert role.name == role_name
    
    retrieved = await role_repo.get_by_id(role.id)
    assert retrieved is not None
    assert retrieved.name == role_name
    
    # Update
    retrieved.description = "Updated desc"
    await role_repo.update(retrieved)
    await db_session.commit()
        
    updated = await role_repo.get_by_id(role.id)
    assert updated.description == "Updated desc"
    
    # Delete
    await role_repo.delete(updated.id)
    await db_session.commit()
        
    deleted = await role_repo.get_by_id(role.id)
    assert deleted is None

@pytest.mark.asyncio
async def test_sqlalchemy_role_repository_list(db_session: AsyncSession) -> None:
    role_repo = SQLAlchemyRoleRepository(db_session)
    role_name_1 = f"integration_role_{uuid.uuid4().hex[:8]}"
    role_name_2 = f"integration_role_{uuid.uuid4().hex[:8]}"
    
    role1 = Role(name=role_name_1, display_name="Role 1", is_active=True)
    role2 = Role(name=role_name_2, display_name="Role 2", is_active=True)
    
    await role_repo.create(role1)
    await role_repo.create(role2)
    await db_session.commit()
        
    roles, total = await role_repo.list_roles()
    assert total >= 2
    
    found_roles = [r for r in roles if r.name in [role_name_1, role_name_2]]
    assert len(found_roles) == 2
    
    await role_repo.delete(role1.id)
    await role_repo.delete(role2.id)
    await db_session.commit()
