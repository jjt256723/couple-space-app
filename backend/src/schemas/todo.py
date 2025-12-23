from pydantic import BaseModel, Field
from datetime import datetime


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    due_date: datetime | None = None


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None
    due_date: datetime | None = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    is_completed: bool
    due_date: datetime | None = None
    user_id: int
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
