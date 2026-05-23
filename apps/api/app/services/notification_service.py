import json
from collections import defaultdict
from uuid import UUID

import redis.asyncio as redis
from fastapi import WebSocket

from app.core.config import settings
from app.observability.metrics import WEBSOCKET_ACTIVE_CONNECTIONS


class WebSocketManager:
    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, organization_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        org_key = str(organization_id)
        self.connections[org_key].add(websocket)
        WEBSOCKET_ACTIVE_CONNECTIONS.labels(org_key).set(len(self.connections[org_key]))

    def disconnect(self, organization_id: UUID, websocket: WebSocket) -> None:
        org_key = str(organization_id)
        self.connections[org_key].discard(websocket)
        WEBSOCKET_ACTIVE_CONNECTIONS.labels(org_key).set(len(self.connections[org_key]))

    async def broadcast(self, organization_id: UUID, payload: dict) -> None:
        stale: list[WebSocket] = []
        for websocket in self.connections[str(organization_id)]:
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(organization_id, websocket)


manager = WebSocketManager()


async def publish_notification(organization_id: UUID, payload: dict) -> None:
    client = redis.from_url(settings.redis_url, decode_responses=True)
    await client.publish(f"org:{organization_id}:events", json.dumps(payload))
    await client.aclose()
