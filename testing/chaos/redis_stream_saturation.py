from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import redis.asyncio as redis


async def main() -> None:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    stream = os.getenv("REDIS_STREAM", "ai-events")
    count = int(os.getenv("CHAOS_EVENT_COUNT", "1000"))
    client = redis.from_url(redis_url, decode_responses=True)
    for index in range(count):
        await client.xadd(stream, {"event_id": str(uuid4()), "event_type": "chaos_probe", "index": index})
    await client.aclose()
    print(f"published={count} stream={stream}")


if __name__ == "__main__":
    asyncio.run(main())
