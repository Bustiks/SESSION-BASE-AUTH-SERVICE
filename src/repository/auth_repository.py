from sqlalchemy import select
from src.models.user import UserORM
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.auth import RegistrationRequest

class AuthRepository:

    @staticmethod
    async def _get_by_email(db: AsyncSession, email: str) -> UserORM | None:
        exists = await db.execute(
            select(UserORM).where(UserORM.email == email)
        )
        return exists.scalars().first()
    
    @staticmethod
    async def create_new_user(db: AsyncSession, data: RegistrationRequest):
        new_user = UserORM(
            email=data.email,
            username=data.username,
            password=data.password
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user