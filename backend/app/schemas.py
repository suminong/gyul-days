from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EntryCreate(BaseModel):
    content: str


class EntryUpdate(BaseModel):
    content: str | None = None


class EntryResponse(BaseModel):
    id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
    )

    email: str = Field(
        min_length=5,
        max_length=320,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)