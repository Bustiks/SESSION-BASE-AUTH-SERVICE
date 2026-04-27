from pydantic import BaseModel, EmailStr, ConfigDict
from src.utils.annotated import Locale

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    username: str
    locale: Locale | None = None