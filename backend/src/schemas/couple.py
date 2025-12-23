from pydantic import BaseModel
from datetime import datetime


class CoupleCreate(BaseModel):
    invite_code: str


class CoupleResponse(BaseModel):
    id: int
    invite_code: str
    anniversary_date: datetime | None = None
    theme_color: str

    class Config:
        from_attributes = True


class CoupleBind(BaseModel):
    invite_code: str
