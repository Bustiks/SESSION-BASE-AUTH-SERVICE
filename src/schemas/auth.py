from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.schemas.user import UserRead

class RegistrationRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=4)

class RegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user: UserRead

class LoginRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user: UserRead