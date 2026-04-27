from src.models.user import UserORM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> UserORM | None:
        result = await db.execute(
            select(UserORM).where(UserORM.id == user_id)
        )
        return result.scalar_one_or_none()