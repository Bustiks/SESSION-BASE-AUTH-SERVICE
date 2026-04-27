from typing import AsyncGenerator
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import UserORM
from src.repository.user_repository import UserRepository
from src.database.database import async_session
from src.database.redis import redis_client
from src.database.config import settings
from redis.asyncio import Redis

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def get_redis() -> Redis:
    return redis_client

async def get_current_user(db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis), 
                           session_id: str = Cookie(default=None, alias=settings.SESSION_COOKIE_NAME)) -> UserORM:
    if not session_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    
    user_id = await redis.get(f"session:{session_id}")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired or invalid")
    
    user = await UserRepository.get_user(db, int(user_id))

    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    
    return user