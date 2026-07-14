from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime, date

from app.domain.entities.login_history import LoginHistory
from app.domain.repositories.login_history_repository import LoginHistoryRepository
from app.infrastructure.repositories.base_repository import SQLAlchemyBaseRepository
from app.domain.enums.login_result import LoginResult

class SQLAlchemyLoginHistoryRepository(SQLAlchemyBaseRepository[LoginHistory], LoginHistoryRepository):
    
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, LoginHistory)

    async def list_by_user(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> tuple[list[LoginHistory], int]:
        stmt_count = select(func.count(LoginHistory.id)).where(LoginHistory.user_id == user_id)
        total = (await self.session.execute(stmt_count)).scalar_one()

        stmt_items = (
            select(LoginHistory)
            .where(LoginHistory.user_id == user_id)
            .order_by(LoginHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list((await self.session.execute(stmt_items)).scalars().all())
        
        return items, total

    async def get_today_login_count(self) -> int:
        today = date.today()
        stmt = select(func.count(LoginHistory.id)).where(
            func.date(LoginHistory.created_at) == today,
            LoginHistory.result == LoginResult.SUCCESS
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def get_today_failed_login_count(self) -> int:
        today = date.today()
        stmt = select(func.count(LoginHistory.id)).where(
            func.date(LoginHistory.created_at) == today,
            LoginHistory.result != LoginResult.SUCCESS
        )
        return (await self.session.execute(stmt)).scalar_one()
