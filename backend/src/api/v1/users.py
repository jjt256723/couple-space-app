from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models import User
from src.schemas.user import UserResponse, UserUpdate
from src.api.dependencies import UserIdDep

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


@router.put("/me", response_model=UserResponse)
async def update_user(
    user_data: UserUpdate,
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if user_data.nickname is not None:
        user.nickname = user_data.nickname
    if user_data.avatar_url is not None:
        user.avatar_url = user_data.avatar_url
    if user_data.bio is not None:
        user.bio = user_data.bio

    await db.commit()
    await db.refresh(user)

    return user
