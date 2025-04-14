from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class Gender(str, Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'


class Client(BaseModel):
    model_config = ConfigDict(validate_default=True)

    client_id: UUID
    login: str | None = None
    age: int | None = Field(default=None, ge=0)
    location: str | None = None
    gender: Gender | None = None
