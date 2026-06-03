"""Stream Processor - Process streaming events with Redis Streams."""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import UUID, uuid4

from app.core.redis import get_redis_client
from app.observability.metrics import (
    REDIS_STREAM_CONSUMER_LAG,
    REDIS_STREAM_EVENTS_CONSUMED_TOTAL,
    REDIS_STREAM_EVENTS_PUBLISHED_TOTAL,
)
from app.observability.tracing import get_tracer


tracer = get_tracer(__name__)


class StreamEventType(str, Enum):
    """Types of stream events."""

    RESUME_UPLOADED = "resume_uploaded"
    CANDIDATE_CREATED = "candidate_created"
    RANKING_UPDATED = "ranking_updated"
    FEEDBACK_RECEIVED = "feedback_received"
    JOB_POSTED = "job_posted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    AI_RESPONSE_GENERATED = "ai_response_generated"


@dataclass
class StreamEvent:
    """Event in a stream."""

    event_id: UUID
    event_type: StreamEventType
    data: dict[str, Any]
    timestamp: datetime
    organization_id: UUID
    user_id: Optional[UUID]


class StreamProcessor:
    """Process events from Redis Streams."""

    def __init__(
        self,
        stream_name: str = "ai_events",
        consumer_group: str = "ai_processors",
        consumer_name: Optional[str] = None,
    ) -> None:
        """Initialize stream processor.

        Args:
            stream_name: Name of the Redis stream
            consumer_group: Name of the consumer group
            consumer_name: Unique consumer name
        """
        self.stream_name = stream_name
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name or f"consumer_{uuid4()}"
        self.handlers: dict[StreamEventType, Callable] = {}
        self.running = False

    async def initialize(self) -> None:
        """Initialize the stream and consumer group."""
        try:
            redis = get_redis_client()
            # Create consumer group if it doesn't exist
            try:
                await redis.xgroup_create(
                    self.stream_name,
                    self.consumer_group,
                    id="0",
                    mkstream=True,
                )
            except Exception:
                # Group might already exist
                pass
        except Exception as e:
            raise RuntimeError(f"Failed to initialize stream: {e}")

    def register_handler(
        self,
        event_type: StreamEventType,
        handler: Callable[[StreamEvent], Any],
    ) -> None:
        """Register a handler for an event type.

        Args:
            event_type: Event type to handle
            handler: Handler function
        """
        self.handlers[event_type] = handler

    async def publish_event(self, event: StreamEvent) -> str:
        """Publish an event to the stream.

        Args:
            event: Event to publish

        Returns:
            Event ID
        """
        try:
            redis = get_redis_client()
            event_data = {
                "event_id": str(event.event_id),
                "event_type": event.event_type.value,
                "data": json.dumps(event.data),
                "timestamp": event.timestamp.isoformat(),
                "organization_id": str(event.organization_id),
                "user_id": str(event.user_id) if event.user_id else "",
            }
            result = await redis.xadd(self.stream_name, event_data)
            REDIS_STREAM_EVENTS_PUBLISHED_TOTAL.labels(
                self.stream_name,
                event.event_type.value,
            ).inc()
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to publish event: {e}")

    async def process_events(
        self,
        batch_size: int = 10,
        block_ms: int = 1000,
    ) -> None:
        """Process events from the stream.

        Args:
            batch_size: Number of events to process per batch
            block_ms: Block time in milliseconds
        """
        self.running = True

        while self.running:
            try:
                redis = get_redis_client()

                # Read events from stream
                events = await redis.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams={self.stream_name: ">"},
                    count=batch_size,
                    block=block_ms,
                )

                if not events:
                    continue

                for stream, event_list in events:
                    for event_id, event_data in event_list:
                        await self._process_single_event(event_id, event_data)

                        # Acknowledge processing
                        await redis.xack(self.stream_name, self.consumer_group, event_id)

            except Exception:
                # Log error and continue
                await asyncio.sleep(1)

    async def _process_single_event(self, event_id: str, event_data: dict) -> None:
        """Process a single event.

        Args:
            event_id: Event ID
            event_data: Event data dictionary
        """
        try:
            with tracer.start_as_current_span("redis_stream.process_event") as span:
                event_type = StreamEventType(self._decode(event_data, "event_type"))
                data = json.loads(self._decode(event_data, "data"))
                span.set_attribute("redis.stream", self.stream_name)
                span.set_attribute("redis.event_id", event_id)
                span.set_attribute("event.type", event_type.value)

                event = StreamEvent(
                    event_id=UUID(self._decode(event_data, "event_id")),
                    event_type=event_type,
                    data=data,
                    timestamp=datetime.fromisoformat(self._decode(event_data, "timestamp")),
                    organization_id=UUID(self._decode(event_data, "organization_id")),
                    user_id=UUID(self._decode(event_data, "user_id")) if self._decode(event_data, "user_id") else None,
                )

                handler = self.handlers.get(event_type)
                if handler:
                    await handler(event)
                REDIS_STREAM_EVENTS_CONSUMED_TOTAL.labels(
                    self.stream_name,
                    self.consumer_group,
                    event_type.value,
                    "success",
                ).inc()

        except Exception as exc:
            REDIS_STREAM_EVENTS_CONSUMED_TOTAL.labels(
                self.stream_name,
                self.consumer_group,
                "unknown",
                "error",
            ).inc()
            raise exc

    async def stop(self) -> None:
        """Stop processing events."""
        self.running = False

    async def get_pending_count(self) -> int:
        """Get count of pending events.

        Returns:
            Number of pending events
        """
        try:
            redis = get_redis_client()
            info = await redis.xinfo_groups(self.stream_name)
            for group_info in info:
                name = self._decode(group_info, "name")
                if name == self.consumer_group:
                    pending = int(group_info.get("pending") or group_info.get(b"pending") or 0)
                    REDIS_STREAM_CONSUMER_LAG.labels(self.stream_name, self.consumer_group).set(pending)
                    return pending
        except Exception:
            pass
        return 0

    @staticmethod
    def _decode(payload: dict, key: str) -> str:
        value = payload.get(key) or payload.get(key.encode())
        if isinstance(value, bytes):
            return value.decode()
        return str(value or "")
