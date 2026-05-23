from __future__ import annotations

import asyncio
import os

import websockets


async def connect_once(url: str) -> None:
    async with websockets.connect(url) as websocket:
        await websocket.send("ping")
        await asyncio.sleep(5)


async def main() -> None:
    organization_id = os.getenv("ORGANIZATION_ID", "00000000-0000-0000-0000-000000000000")
    ws_url = os.getenv("WS_URL", f"ws://localhost:8000/api/v1/ws/{organization_id}")
    connections = int(os.getenv("WS_CONNECTIONS", "100"))
    await asyncio.gather(*(connect_once(ws_url) for _ in range(connections)))


if __name__ == "__main__":
    asyncio.run(main())
