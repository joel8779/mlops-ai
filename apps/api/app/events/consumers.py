from app.logging import get_logger
from app.events.event_bus import RedisStreamEventBus

logger = get_logger(__name__)


async def consume_organization_events(stream: str, group: str, consumer: str) -> None:
    bus = RedisStreamEventBus()
    events = await bus.consume(stream, group, consumer)
    for event in events:
        try:
            logger.info("domain_event_consumed", event_type=event.type.value, organization_id=str(event.organization_id))
        except Exception as exc:
            await bus.dead_letter(event, str(exc))
