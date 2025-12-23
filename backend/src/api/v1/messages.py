from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from src.core.database import get_db
from src.models import User, Message, Room
from src.schemas.message import MessageCreate, MessageResponse
from src.api.dependencies import UserIdDep

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    sender_id: UserIdDep,
    db: AsyncSession = Depends(get_db),
):
    sender_result = await db.execute(select(User).where(User.id == sender_id))
    sender = sender_result.scalar_one_or_none()
    if not sender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="发送者不存在"
        )

    if not sender.couple_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未绑定情侣关系"
        )

    partner_result = await db.execute(
        select(User).where(User.couple_id == sender.couple_id, User.id != sender.id)
    )
    partner = partner_result.scalar_one_or_none()

    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="伴侣不存在"
        )

    room_result = await db.execute(
        select(Room).where(Room.couple_id == sender.couple_id)
    )
    room = room_result.scalar_one_or_none()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="聊天房间不存在"
        )

    new_message = Message(
        content=message_data.content,
        message_type=message_data.message_type,
        sender_id=sender_id,
        receiver_id=partner.id,
        room_id=room.id,
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    return new_message


@router.get("", response_model=List[MessageResponse])
async def get_messages(
    user_id: UserIdDep,
    skip: int = 0,
    limit: int = 50,
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
        select(Message)
        .where(
            (Message.sender_id == user_id) | (Message.receiver_id == user_id)
        )
        .order_by(desc(Message.created_at))
        .offset(skip)
        .limit(limit)
    )
    messages = result.scalars().all()
    return list(reversed(messages))


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在"
        )
    return message
