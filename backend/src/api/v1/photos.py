from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from core.database import get_db
from models import User, Photo
from schemas.photo import PhotoCreate, PhotoResponse
from api.dependencies import UserIdDep

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    user_id: UserIdDep,
    file: UploadFile = File(...),
    caption: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    url = f"https://placeholder.com/photos/{file.filename}"
    thumbnail_url = f"https://placeholder.com/photos/thumb_{file.filename}"

    new_photo = Photo(
        filename=file.filename,
        url=url,
        thumbnail_url=thumbnail_url,
        caption=caption,
        user_id=user.id,
    )
    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)

    return new_photo


@router.get("", response_model=List[PhotoResponse])
async def get_photos(
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
        return []

    result = await db.execute(
        select(Photo)
        .where(User.couple_id == user.couple_id)
        .order_by(desc(Photo.created_at))
        .offset(skip)
        .limit(limit)
    )
    photos = result.scalars().all()
    return list(photos)


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: int,
    user_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="照片不存在"
        )

    if photo.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此照片"
        )

    await db.delete(photo)
    await db.commit()

    return None
