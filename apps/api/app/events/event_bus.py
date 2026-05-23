import json
from typing import Protocol

import redis.asyncio as redis

from app.core.config import settings
from app.events.types import DomainEvent


class EventBus(Protocol):
    async def publish(self, stream: str, event: DomainEvent) -> str:
        ...


class RedisStreamEventBus:
    def __init__(self) -> None:
        self.client = redis.from_url(settings.redis_url, decode_responses=True)

    async def publish(self, stream: str, event: DomainEvent) -> str:
        return await self.client.xadd(
            stream,
            {"event": event.model_dump_json()},
            maxlen=100000,
            approximate=True,
        )

    async def consume(self, stream: str, group: str, consumer: str, count: int = 10) -> list[DomainEvent]:
        try:
            await self.client.xgroup_create(stream, group, id="0", mkstream=True)
        except Exception:
            pass
        messages = await self.client.xreadgroup(group, consumer, {stream: ">"}, count=count, block=1000)
        events: list[DomainEvent] = []
        for _, stream_messages in messages:
            for _, values in stream_messages:
                events.append(DomainEvent.model_validate(json.loads(values["event"])))
        return events

    async def dead_letter(self, event: DomainEvent, reason: str) -> None:
        await self.publish("events.dead_letter", event.model_copy(update={"payload": {**event.payload, "reason": reason}}))


def get_event_bus() -> RedisStreamEventBus:
    return RedisStreamEventBus()
