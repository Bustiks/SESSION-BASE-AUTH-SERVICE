import datetime
import enum
from typing import Annotated
from sqlalchemy import DateTime, text
from sqlalchemy.orm import mapped_column

int_id = Annotated[int, mapped_column(primary_key=True)]

created_at = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC)
    )
]

updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC)
    )
]

class Locale(enum.Enum):
    ru = "ru-RU"
    en = "en-US"