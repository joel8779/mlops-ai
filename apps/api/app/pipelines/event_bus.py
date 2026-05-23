"""Event Bus - Pub/Sub event system for real-time communication."""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from uuid import UUID

from app.core.redis import get_redis_client


class Channel(str, Enum):
    """Pub/Sub channels."""

    CANDIDATE_UPDATES = "candidate:updates"
    RANKING_UPDATES = "ranking:updates"
    AI_RESPONSES = "ai:responses"
    NOTIFICATIONS = "notifications"
    WEBHOOK_EVENTS = "webhook:events"


@dataclass
class Event:
    """Event message."""

    event_id: UUID
    channel: Channel
    data: dict[str, Any]
    timestamp: datetime
    organization_id: UUID


class EventBus:
    """Event bus for pub/sub messaging."""

    def __init__(self) -> None:
        """Initialize event bus."""
        self.subscribers: dict[Channel, list[Callable]] = {}
        self.running = False

    async def publish(self, event: Event) -> None:
        """Publish an event to a channel.

        Args:
            event: Event to publish
        """
        try:
            redis = get_redis_client()
            message = {
                "event_id": str(event.event_id),
                "channel": event.channel.value,
                "data": json.dumps(event.data),
                "timestamp": event.timestamp.isoformat(),
                "organization_id": str(event.organization_id),
            }
            await redis.publish(event.channel.value, json.dumps(message))
        except Exception as e:
            raise RuntimeError(f"Failed to publish event: {e}")

    async def subscribe(
        self,
        channel: Channel,
        handler: Callable[[Event], Any],
    ) -> None:
        """Subscribe to a channel.

        Args:
            channel: Channel to subscribe to
            handler: Handler function
        """
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(handler)

    async def start_listening(self) -> None:
        """Start listening to subscribed channels."""
        self.running = True

        while self.running:
            try:
                redis = get_redis_client()
                pubsub = redis.pubsub()

                # Subscribe to all channels
                for channel in self.subscribers.keys():
                    await pubsub.subscribe(channel.value)

                async for message in pubsub.listen():
                    if message["type"] == "message":
                        await self._handle_message(message)

            except Exception as e:
                await asyncio.sleep(1)

    async def _handle_message(self, message: dict) -> None:
        """Handle a received message.

        Args:
            message: Redis pub/sub message
        """
        try:
            data = json.loads(message["data"])
            channel = Channel(data["channel"])

            event = Event(
                event_id=UUID(data["event_id"]),
                channel=channel,
                data=json.loads(data["data"]),
                timestamp=datetime.fromisoformat(data["timestamp"]),
                organization_id=UUID(data["organization_id"]),
            )

            # Call all subscribers for this channel
            handlers = self.subscribers.get(channel, [])
            for handler in handlers:
                await handler(event)

        except Exception as e:
            # Log error
            pass

    def stop(self) -> None:
        """Stop listening to channels."""
        self.running = False
