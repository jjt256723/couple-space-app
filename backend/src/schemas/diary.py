from pydantic import BaseModel, Field
from datetime import datetime


class DiaryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    mood: str | None = None


class DiaryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    mood: str | None = None


class DiaryResponse(BaseModel):
    id: int
    title: str
    content: str
    mood: str | None = None
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
