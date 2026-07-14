import pytest
import uuid
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.permission import Permission
from app.domain.enums.permission_module import PermissionModule
from app.infrastructure.repositories.permission_repository import SQLAlchemyPermissionRepository

@pytest.mark.asyncio
async def test_sqlalchemy_permission_repository_list_and_get_by_ids(db_session: AsyncSession) -> None:
    perm_repo = SQLAlchemyPermissionRepository(db_session)
    perm_name_1 = f"perm1_{uuid.uuid4().hex[:8]}"
    perm_name_2 = f"perm2_{uuid.uuid4().hex[:8]}"
    
    p1 = Permission(name=perm_name_1, module=PermissionModule.AUTH, description="Perm 1", is_active=True)
    p2 = Permission(name=perm_name_2, module=PermissionModule.USERS, description="Perm 2", is_active=True)
    
    db_session.add(p1)
    db_session.add(p2)
    await db_session.commit()
        
    permissions = await perm_repo.get_all()
    assert len(permissions) >= 2
    
    found_names = [p.name for p in permissions]
    assert perm_name_1 in found_names
    assert perm_name_2 in found_names
    
    perms_by_ids = await perm_repo.get_by_ids([p1.id, p2.id])
    assert len(perms_by_ids) == 2
    
    await db_session.execute(delete(Permission).where(Permission.id.in_([p1.id, p2.id])))
    await db_session.commit()
