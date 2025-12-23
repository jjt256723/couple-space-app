from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from core.database import get_db
from core.security import create_access_token
from models import User, Room, Couple
from schemas.user import UserResponse
from schemas.couple import CoupleCreate, CoupleResponse, CoupleBind
import secrets
from datetime import datetime
from api.dependencies import UserIdDep

router = APIRouter(prefix="/couples", tags=["couples"])


@router.post("", response_model=CoupleResponse, status_code=status.HTTP_201_CREATED)
async def create_couple(
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if user.couple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已绑定情侣关系"
        )

    invite_code = secrets.token_hex(10)

    new_couple = Couple(
        invite_code=invite_code,
        anniversary_date=None,
    )
    db.add(new_couple)
    await db.commit()
    await db.refresh(new_couple)

    user.couple_id = new_couple.id

    new_room = Room(name="聊天室", couple_id=new_couple.id)
    db.add(new_room)
    await db.commit()

    return new_couple


@router.post("/bind", response_model=CoupleResponse)
async def bind_couple(
    bind_data: CoupleBind,
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if user.couple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已绑定情侣关系"
        )

    couple_result = await db.execute(
        select(Couple).where(Couple.invite_code == bind_data.invite_code)
    )
    couple = couple_result.scalar_one_or_none()
    if not couple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请码无效"
        )

    users_count = await db.execute(
        select(User).where(User.couple_id == couple.id)
    )
    if users_count.scalars().count() >= 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该情侣关系已满员"
        )

    user.couple_id = couple.id
    await db.commit()
    await db.refresh(user)

    return couple


@router.get("", response_model=CoupleResponse)
async def get_couple(
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if not user.couple_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未绑定情侣关系"
        )

    couple_result = await db.execute(select(Couple).where(Couple.id == user.couple_id))
    couple = couple_result.scalar_one_or_none()
    if not couple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="情侣关系不存在"
        )

    return couple


@router.get("/partner", response_model=UserResponse)
async def get_partner(
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if not user.couple_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未绑定情侣关系"
        )

    partner_result = await db.execute(
        select(User).where(User.couple_id == user.couple_id, User.id != user_id)
    )
    partner = partner_result.scalar_one_or_none()

    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="伴侣不存在"
        )

    return partner
