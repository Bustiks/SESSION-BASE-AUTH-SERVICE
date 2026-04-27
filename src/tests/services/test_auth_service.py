from fastapi import HTTPException
from redis.asyncio import Redis
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.user import UserRead
from src.schemas.auth import RegistrationRequest, RegistrationResponse, LoginRequest, LoginResponse
from src.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_user_success_registration(db: AsyncSession, redis: Redis):
    result, session_id = await AuthService.registration(
        db, RegistrationRequest(email="example238@gmail.com", username="test_username", password="fake_password"),
        redis
    )

    assert isinstance(result, RegistrationResponse)
    assert result.user.username == "test_username"
    assert isinstance(session_id, str)
    assert await redis.exists(f"session:{session_id}") == 1


@pytest.mark.asyncio
async def test_user_unsuccess_registration(db: AsyncSession, redis: Redis):
    await AuthService.registration(
        db,
        RegistrationRequest(email="example238@gmail.com", username="test_username", password="fake_password"),
        redis
    )

    with pytest.raises(HTTPException) as exc_info:
        await AuthService.registration(
            db,
            RegistrationRequest(email="example238@gmail.com", username="test_username", password="fake_password"),
            redis
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "User already exists"


@pytest.mark.asyncio
async def test_user_success_login(db: AsyncSession, redis: Redis):
    await AuthService.registration(
        db,
        RegistrationRequest(email="example238@gmail.com", username="test_username", password="fake_password"),
        redis
    )

    result, session_id = await AuthService.login(
        db,
        LoginRequest(email="example238@gmail.com", password="fake_password"),
        redis
    )

    assert isinstance(result, LoginResponse)
    assert isinstance(result.user, UserRead)
    assert result.user.username == "test_username"
    assert result.user.email == "example238@gmail.com"
    assert isinstance(session_id, str)
    assert await redis.exists(f"session:{session_id}") == 1


@pytest.mark.asyncio
async def test_user_unsuccess_login_with_password(db: AsyncSession, redis: Redis):
    await AuthService.registration(
        db,
        RegistrationRequest(email="example238@gmail.com", username="test_username", password="fake_password"),
        redis
    )

    with pytest.raises(HTTPException) as exc_info:
        await AuthService.login(
            db,
            LoginRequest(email="example238@gmail.com", password="fake_password_fake_password"),
            redis
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid username or password"


@pytest.mark.asyncio
async def test_user_unsuccess_login_with_email(db: AsyncSession, redis: Redis):
    await AuthService.registration(
        db,
        RegistrationRequest(email="example238@gmail.com", username="test_username", password="fake_password"),
        redis
    )

    with pytest.raises(HTTPException) as exc_info:
        await AuthService.login(
            db,
            LoginRequest(email="example888@gmail.com", password="fake_password"),
            redis
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid username or password"


@pytest.mark.asyncio
async def test_user_logout(db: AsyncSession, redis: Redis):
    _, session_id = await AuthService.registration(
        db,
        RegistrationRequest(email="example238@gmail.com", username="test_username", password="fake_password"),
        redis
    )

    assert await redis.exists(f"session:{session_id}") == 1

    await AuthService.logout(redis, session_id)

    assert await redis.exists(f"session:{session_id}") == 0
