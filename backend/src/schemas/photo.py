from pydantic import BaseModel, Field
from datetime import datetime


class PhotoCreate(BaseModel):
    caption: str | None = None


class PhotoResponse(BaseModel):
    id: int
    filename: str
    url: str
    thumbnail_url: str | None = None
    caption: str | None = None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
