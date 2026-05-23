from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.notification_service import manager

router = APIRouter()


@router.websocket("/ws/{organization_id}")
async def websocket_events(websocket: WebSocket, organization_id: UUID):
    await manager.connect(organization_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(organization_id, websocket)
