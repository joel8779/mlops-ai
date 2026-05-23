from app.events.event_bus import get_event_bus
from app.events.types import DomainEvent


async def publish_domain_event(event: DomainEvent) -> None:
    await get_event_bus().publish(f"org:{event.organization_id}:events", event)
