from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nickname: str = Field(..., min_length=1, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: str
    avatar_url: str | None = None
    bio: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None
    bio: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: int
    exp: int
