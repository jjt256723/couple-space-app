from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from src.core.database import get_db
from src.models import User, Room, Message
from src.websocket.manager import manager, get_current_user_ws
from src.schemas.message import MessageCreate, MessageResponse
from datetime import datetime

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    current_user = await get_current_user_ws(token, db)
    if not current_user:
        await websocket.close(code=4001, reason="无效的认证凭据")
        return

    user_id = current_user.id

    await manager.connect(websocket, user_id)

    if current_user.couple_id:
        result = await db.execute(
            select(Room).where(Room.couple_id == current_user.couple_id)
        )
        room = result.scalar_one_or_none()

        if room:
            manager.join_room(user_id, room.id)

            await manager.send_personal(
                {
                    "type": "connected",
                    "message": "已连接到聊天室",
                    "room_id": room.id,
                },
                user_id
            )

            await manager.broadcast_to_room(
                {
                    "type": "user_online",
                    "user_id": user_id,
                    "username": current_user.username,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                room.id,
                exclude_user_id=user_id
            )

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            message_type = message_data.get("type")

            if message_type == "ping":
                await manager.send_personal(
                    {"type": "pong", "timestamp": datetime.utcnow().isoformat()},
                    user_id
                )

            elif message_type == "send_message":
                content = message_data.get("content")
                msg_type = message_data.get("message_type", "text")
                room_id = message_data.get("room_id")

                if not content or not room_id:
                    await manager.send_personal(
                        {"type": "error", "message": "消息内容或房间ID不能为空"},
                        user_id
                    )
                    continue

                if current_user.couple_id:
                    partner_result = await db.execute(
                        select(User).where(
                            User.couple_id == current_user.couple_id,
                            User.id != user_id
                        )
                    )
                    partner = partner_result.scalar_one_or_none()

                    room_result = await db.execute(
                        select(Room).where(Room.id == room_id, Room.couple_id == current_user.couple_id)
                    )
                    room = room_result.scalar_one_or_none()

                    if partner and room:
                        new_message = Message(
                            content=content,
                            message_type=msg_type,
                            sender_id=user_id,
                            receiver_id=partner.id,
                            room_id=room.id,
                        )
                        db.add(new_message)
                        await db.commit()
                        await db.refresh(new_message)

                        message_response = {
                            "type": "new_message",
                            "message": {
                                "id": new_message.id,
                                "content": new_message.content,
                                "message_type": new_message.message_type,
                                "sender_id": new_message.sender_id,
                                "receiver_id": new_message.receiver_id,
                                "room_id": new_message.room_id,
                                "created_at": new_message.created_at.isoformat(),
                            }
                        }

                        await manager.send_personal(message_response, user_id)
                        await manager.broadcast_to_room(message_response, room.id, exclude_user_id=user_id)

            elif message_type == "typing":
                room_id = message_data.get("room_id")
                is_typing = message_data.get("is_typing", False)

                if current_user.couple_id and room_id:
                    await manager.broadcast_to_room(
                        {
                            "type": "user_typing",
                            "user_id": user_id,
                            "is_typing": is_typing,
                        },
                        room_id,
                        exclude_user_id=user_id
                    )

            elif message_type == "read_receipt":
                message_id = message_data.get("message_id")

                if current_user.couple_id:
                    result = await db.execute(
                        select(Room).where(Room.couple_id == current_user.couple_id)
                    )
                    room = result.scalar_one_or_none()
                    if room:
                        await manager.broadcast_to_room(
                            {
                                "type": "message_read",
                                "message_id": message_id,
                                "user_id": user_id,
                            },
                            room.id,
                            exclude_user_id=user_id
                        )

    except WebSocketDisconnect:
        manager.disconnect(user_id)

        if current_user.couple_id:
            result = await db.execute(
                select(Room).where(Room.couple_id == current_user.couple_id)
            )
            room = result.scalar_one_or_none()

            if room:
                manager.leave_room(user_id, room.id)

                await manager.broadcast_to_room(
                    {
                        "type": "user_offline",
                        "user_id": user_id,
                        "username": current_user.username,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    room.id
                )

    except Exception as e:
        manager.disconnect(user_id)
        await websocket.close(code=4000, reason=f"发生错误: {str(e)}")
