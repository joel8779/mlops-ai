import json
from collections import defaultdict
from uuid import UUID

import redis.asyncio as redis
from fastapi import WebSocket

from app.core.config import settings


class WebSocketManager:
    def __init__(self) -> None:
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, organization_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[str(organization_id)].add(websocket)

    def disconnect(self, organization_id: UUID, websocket: WebSocket) -> None:
        self.connections[str(organization_id)].discard(websocket)

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
