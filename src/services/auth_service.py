import uuid
import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.database.config import settings
from src.schemas.auth import RegistrationRequest, RegistrationResponse, LoginRequest, LoginResponse
from src.schemas.user import UserRead
from src.repository.auth_repository import AuthRepository
from src.utils.logging import log_service
from pwdlib import PasswordHash

logger = logging.getLogger(__name__)
hasher = PasswordHash.recommended()

class AuthService:

    @staticmethod
    @log_service(logger=logger, log_result=True)
    async def registration(db: AsyncSession, data: RegistrationRequest, redis: Redis) -> RegistrationResponse:
        existing = await AuthRepository._get_by_email(db, data.email)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "User already exists")
        
        data.password = hasher.hash(data.password)
        user = await AuthRepository.create_new_user(db, data)

        session_id = str(uuid.uuid4())
        await redis.set(f"session:{session_id}", user.id, ex=settings.SESSION_TTL_SECONDS)

        return RegistrationResponse(user=UserRead.model_validate(user)), session_id
    
    @staticmethod
    @log_service(logger=logger, log_result=True)
    async def login(db: AsyncSession, data: LoginRequest, redis: Redis) -> LoginResponse:
        user = await AuthRepository._get_by_email(db, data.email)

        if not user or not hasher.verify(data.password, user.password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")
        
        session_id = str(uuid.uuid4())
        await redis.set(f"session:{session_id}", user.id, ex=settings.SESSION_TTL_SECONDS)

        return LoginResponse(user=UserRead.model_validate(user)), session_id
    
    @staticmethod
    @log_service(logger=logger, log_result=True)
    async def logout(redis: Redis, session_id: str) -> None:
        await redis.delete(f"session:{session_id}")