from fastapi import APIRouter, Depends
from models.user import UserORM
from schemas.user import UserRead
from src.utils.dependencies import get_current_user

user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.get("/me")
async def get_me(user: UserORM = Depends(get_current_user)):
    return UserRead.model_validate(user)