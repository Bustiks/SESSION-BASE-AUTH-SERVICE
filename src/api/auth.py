from fastapi import APIRouter, Cookie, Depends, Response
from redis.asyncio import Redis
from src.schemas.auth import RegistrationResponse, RegistrationRequest, LoginResponse, LoginRequest
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.auth_service import AuthService
from src.database.config import settings
from src.utils.dependencies import get_db, get_redis

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/registration", response_model=RegistrationResponse)
async def registration(data: RegistrationRequest, response: Response, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    result, session_id = await AuthService.registration(db, data, redis)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        max_age=settings.SESSION_TTL_SECONDS,
    )
    return result

@auth_router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    result, session_id = await AuthService.login(db, data, redis)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        max_age=settings.SESSION_TTL_SECONDS,
    )
    return result

@auth_router.post("/logout")
async def logout(response: Response, redis: Redis = Depends(get_redis), session_id: str = Cookie(default=None, alias=settings.SESSION_COOKIE_NAME)):
    if session_id:
        await AuthService.logout(redis, session_id)
    
    response.delete_cookie(key=settings.SESSION_COOKIE_NAME)
    return {"detail": "Logged out"}

