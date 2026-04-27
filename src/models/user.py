from sqlalchemy import text, Enum

from src.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from src.utils.annotated import int_id, created_at, updated_at, Locale

class UserORM(Base):
    __tablename__ = "user"

    id: Mapped[int_id]
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    locale: Mapped[Locale] = mapped_column(Enum(Locale), nullable=False, name="locale", default=Locale.en, server_default=text("'en'"))
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]