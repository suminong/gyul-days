from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EntryCreate(BaseModel):
    content: str


class EntryUpdate(BaseModel):
    content: str | None = None


class EntryResponse(BaseModel):
    id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)