from pydantic import BaseModel, Field
from datetime import datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: str = "text"


class MessageResponse(BaseModel):
    id: int
    content: str
    message_type: str
    sender_id: int
    receiver_id: int
    room_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MessageSocket(BaseModel):
    content: str
    message_type: str
    room_id: int
