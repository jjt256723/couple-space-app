from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from datetime import datetime

from core.database import get_db
from models import User, Diary
from schemas.diary import DiaryCreate, DiaryUpdate, DiaryResponse
from api.dependencies import UserIdDep

router = APIRouter(prefix="/diaries", tags=["diaries"])


@router.post("", response_model=DiaryResponse, status_code=status.HTTP_201_CREATED)
async def create_diary(
    diary_data: DiaryCreate,
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

    new_diary = Diary(
        title=diary_data.title,
        content=diary_data.content,
        mood=diary_data.mood,
        user_id=user.id,
    )
    db.add(new_diary)
    await db.commit()
    await db.refresh(new_diary)

    return new_diary


@router.get("", response_model=List[DiaryResponse])
async def get_diaries(
    user_id: UserIdDep,
    skip: int = 0,
    limit: int = 20,
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
        result = await db.execute(
            select(Diary)
            .where(Diary.user_id == user_id)
            .order_by(desc(Diary.created_at))
            .offset(skip)
            .limit(limit)
        )
    else:
        result = await db.execute(
            select(Diary)
            .where(User.couple_id == user.couple_id)
            .order_by(desc(Diary.created_at))
            .offset(skip)
            .limit(limit)
        )

    diaries = result.scalars().all()
    return list(diaries)


@router.get("/{diary_id}", response_model=DiaryResponse)
async def get_diary(diary_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Diary).where(Diary.id == diary_id))
    diary = result.scalar_one_or_none()
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日记不存在"
        )
    return diary


@router.put("/{diary_id}", response_model=DiaryResponse)
async def update_diary(
    diary_id: int,
    diary_data: DiaryUpdate,
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Diary).where(Diary.id == diary_id))
    diary = result.scalar_one_or_none()
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日记不存在"
        )

    if diary.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限编辑此日记"
        )

    if diary_data.title is not None:
        diary.title = diary_data.title
    if diary_data.content is not None:
        diary.content = diary_data.content
    if diary_data.mood is not None:
        diary.mood = diary_data.mood

    await db.commit()
    await db.refresh(diary)

    return diary


@router.delete("/{diary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diary(
    diary_id: int,
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Diary).where(Diary.id == diary_id))
    diary = result.scalar_one_or_none()
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日记不存在"
        )

    if diary.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此日记"
        )

    await db.delete(diary)
    await db.commit()

    return None
