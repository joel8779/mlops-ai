from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.observability.metrics import WEBSOCKET_CONNECTIONS
from app.observability.tracing import get_tracer
from app.services.notification_service import manager

router = APIRouter()
tracer = get_tracer(__name__)


@router.websocket("/ws/{organization_id}")
async def websocket_events(websocket: WebSocket, organization_id: UUID):
    with tracer.start_as_current_span("websocket.connect") as span:
        span.set_attribute("organization.id", str(organization_id))
        await manager.connect(organization_id, websocket)
        WEBSOCKET_CONNECTIONS.labels(str(organization_id)).inc()
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(organization_id, websocket)
