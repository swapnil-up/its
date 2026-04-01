from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from ..websocket_manager import manager
from ..core.security import decode_token
from jose import JWTError

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str, token: str=Query(...)):
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return 

    await manager.connect(websocket,room)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)