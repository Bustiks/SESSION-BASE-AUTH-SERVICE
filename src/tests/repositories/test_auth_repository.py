import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.annotated import Locale
from src.models.user import UserORM
from src.repository.auth_repository import AuthRepository
from src.schemas.auth import RegistrationRequest
from src.schemas.user import UserRead

async def _create_test_user(db: AsyncSession, data: RegistrationRequest):
    return await AuthRepository.create_new_user(
        db, data.username, data.password, data.email
    )

@pytest.mark.asyncio
async def test_get_by_username(db: AsyncSession):
    if await _create_test_user(db, RegistrationRequest(email="example238@gmail.com", username="username", password="fake_hashed_password")):
        user = await AuthRepository._get_by_email(db, "example238@gmail.com")

        assert user
        assert user.username == "username"
        assert user.locale == Locale.en
        assert user.id is not None

@pytest.mark.asyncio
async def test_create_new_user(db: AsyncSession):
    created: UserORM = await _create_test_user(
        db,
        RegistrationRequest(email="example238@gmail.com", username="username", password="fake_hashed_password")
    )

    new_created = UserRead.model_validate(created)

    assert new_created.email == "example238@gmail.com"
    assert new_created.username == "username"
    assert new_created.id is not None
    assert new_created.locale == Locale.en