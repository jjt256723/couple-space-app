from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Set
import json

from core.database import get_db
from models import User, Room
from core.security import decode_access_token


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.room_participants: Dict[int, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    def join_room(self, user_id: int, room_id: int):
        if room_id not in self.room_participants:
            self.room_participants[room_id] = set()
        self.room_participants[room_id].add(user_id)

    def leave_room(self, user_id: int, room_id: int):
        if room_id in self.room_participants:
            self.room_participants[room_id].discard(user_id)

    async def send_personal(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))

    async def broadcast_to_room(self, message: dict, room_id: int, exclude_user_id: int = None):
        if room_id not in self.room_participants:
            return

        for user_id in self.room_participants[room_id]:
            if exclude_user_id is None or user_id != exclude_user_id:
                if user_id in self.active_connections:
                    await self.active_connections[user_id].send_text(json.dumps(message))

    def get_room_users(self, room_id: int) -> Set[int]:
        return self.room_participants.get(room_id, set())

    def is_user_online(self, user_id: int) -> bool:
        return user_id in self.active_connections


manager = ConnectionManager()


async def get_current_user_ws(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id: str = payload.get("sub")
    if user_id is None:
        return None

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    return user
