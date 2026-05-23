import json
from typing import Protocol

import redis.asyncio as redis

from app.core.config import settings
from app.events.types import DomainEvent
from app.observability.metrics import REDIS_STREAM_EVENTS_CONSUMED_TOTAL, REDIS_STREAM_EVENTS_PUBLISHED_TOTAL
from app.observability.tracing import get_tracer


tracer = get_tracer(__name__)


class EventBus(Protocol):
    async def publish(self, stream: str, event: DomainEvent) -> str:
        ...


class RedisStreamEventBus:
    def __init__(self) -> None:
        self.client = redis.from_url(settings.redis_url, decode_responses=True)

    async def publish(self, stream: str, event: DomainEvent) -> str:
        with tracer.start_as_current_span("event_bus.publish") as span:
            span.set_attribute("redis.stream", stream)
            span.set_attribute("event.type", event.type.value)
            event_id = await self.client.xadd(
                stream,
                {"event": event.model_dump_json()},
                maxlen=100000,
                approximate=True,
            )
            REDIS_STREAM_EVENTS_PUBLISHED_TOTAL.labels(stream, event.type.value).inc()
            return event_id

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
                REDIS_STREAM_EVENTS_CONSUMED_TOTAL.labels(stream, group, events[-1].type.value, "success").inc()
        return events

    async def dead_letter(self, event: DomainEvent, reason: str) -> None:
        await self.publish("events.dead_letter", event.model_copy(update={"payload": {**event.payload, "reason": reason}}))


def get_event_bus() -> RedisStreamEventBus:
    return RedisStreamEventBus()
