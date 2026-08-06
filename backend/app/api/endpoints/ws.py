from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError
from typing import Optional

from app.core.config import settings
from app.core.websockets import manager
from app.core.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy.future import select

router = APIRouter()

async def get_user_from_token(token: str) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Only allow access_token (no purpose) or waiting_token
        purpose = payload.get("purpose")
        if purpose and purpose != "waiting_verify":
            return None
            
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == username))
        user = result.scalars().first()
        return user

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=1008) # Policy Violation (invalid token)
        return

    await manager.connect(websocket, user.id)
    try:
        while True:
            # We don't expect the client to send messages right now, but we must keep the connection open
            # and handle disconnects
            data = await websocket.receive_text()
            # If we want to handle client->server messages via WS, we can do it here
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
