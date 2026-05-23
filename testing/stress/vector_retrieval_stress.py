from __future__ import annotations

import asyncio
import os
import time
from uuid import UUID

import httpx


async def main() -> None:
    api_url = os.getenv("API_URL", "http://localhost:8000")
    token = os.getenv("API_TOKEN", "")
    organization_id = os.getenv("ORGANIZATION_ID")
    if not organization_id:
        raise SystemExit("Set ORGANIZATION_ID before running vector retrieval stress tests")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    payload = {"query": "senior python mlops kubernetes", "limit": 10}
    async with httpx.AsyncClient(base_url=api_url, headers=headers, timeout=30) as client:
        start = time.perf_counter()
        await asyncio.gather(*(client.post("/api/v1/search/candidates", json=payload) for _ in range(50)))
        print(f"completed=50 duration_seconds={time.perf_counter() - start:.3f} org={UUID(organization_id)}")


if __name__ == "__main__":
    asyncio.run(main())
