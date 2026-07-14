import pytest
import uuid
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.entities.audit_log import AuditLog
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.permission_module import PermissionModule
from app.infrastructure.repositories.audit_repository import SQLAlchemyAuditRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

@pytest.mark.asyncio
async def test_sqlalchemy_audit_repository_crud(db_session: AsyncSession) -> None:
    audit_repo = SQLAlchemyAuditRepository(db_session)
    user_repo = SQLAlchemyUserRepository(db_session)
    
    # 1. Arrange User
    user = User(
        email=f"audit_test_{uuid.uuid4().hex[:8]}@ttms.com",
        username=f"audit_user_{uuid.uuid4().hex[:8]}",
        password_hash="hash",
        first_name="Audit",
        last_name="Tester",
        is_active=True,
    )
    
    created_user = await user_repo.create(user)
    await db_session.commit()
    
    # 2. Arrange Audit Logs
    record_id = uuid.uuid4()
    audit1 = AuditLog(
        user_id=created_user.id,
        action=AuditAction.CREATE,
        module=PermissionModule.USERS,
        table_name="users",
        record_id=record_id,
        new_values={"status": "ACTIVE"}
    )
    
    audit2 = AuditLog(
        user_id=created_user.id,
        action=AuditAction.UPDATE,
        module=PermissionModule.USERS,
        table_name="users",
        record_id=record_id,
        old_values={"status": "ACTIVE"},
        new_values={"status": "INACTIVE"}
    )
    
    # 3. Act
    a1 = await audit_repo.create(audit1)
    a2 = await audit_repo.create(audit2)
    await db_session.commit()
        
    # 4. Assert
    items, total = await audit_repo.list_audit_logs(limit=2)
    assert total >= 2
    assert len(items) == 2
    
    # Cleanup
    await db_session.execute(delete(AuditLog).where(AuditLog.id.in_([a1.id, a2.id])))
    await user_repo.delete(created_user.id)
    await db_session.commit()
