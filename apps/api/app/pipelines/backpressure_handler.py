"""Backpressure Handler - Handle backpressure in streaming pipelines."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class BackpressureStrategy(str, Enum):
    """Backpressure handling strategies."""

    DROP = "drop"
    BLOCK = "block"
    BUFFER = "buffer"
    THROTTLE = "throttle"


@dataclass
class BackpressureMetrics:
    """Backpressure metrics."""

    queue_size: int
    processing_rate: float
    drop_rate: float
    latency_ms: float
    timestamp: datetime


class BackpressureHandler:
    """Handle backpressure in streaming systems."""

    def __init__(
        self,
        max_queue_size: int = 1000,
        strategy: BackpressureStrategy = BackpressureStrategy.BUFFER,
        buffer_size: int = 100,
    ) -> None:
        """Initialize backpressure handler.

        Args:
            max_queue_size: Maximum queue size before triggering backpressure
            strategy: Backpressure strategy
            buffer_size: Size of buffer for BUFFER strategy
        """
        self.max_queue_size = max_queue_size
        self.strategy = strategy
        self.buffer_size = buffer_size
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.buffer = asyncio.Queue(maxsize=buffer_size)
        self.drop_count = 0
        self.process_count = 0
        self.start_time = datetime.now(timezone.utc)

    async def enqueue(self, item: Any) -> bool:
        """Enqueue an item with backpressure handling.

        Args:
            item: Item to enqueue

        Returns:
            True if enqueued, False if dropped
        """
        if self.strategy == BackpressureStrategy.DROP:
            if self.queue.full():
                self.drop_count += 1
                return False
            await self.queue.put(item)
            return True

        elif self.strategy == BackpressureStrategy.BLOCK:
            await self.queue.put(item)
            return True

        elif self.strategy == BackpressureStrategy.BUFFER:
            if self.queue.full():
                if self.buffer.full():
                    self.drop_count += 1
                    return False
                await self.buffer.put(item)
                return True
            await self.queue.put(item)
            return True

        elif self.strategy == BackpressureStrategy.THROTTLE:
            # Add delay before enqueueing
            await asyncio.sleep(0.01)
            if self.queue.full():
                self.drop_count += 1
                return False
            await self.queue.put(item)
            return True

        return False

    async def dequeue(self) -> Optional[Any]:
        """Dequeue an item.

        Returns:
            Item or None
        """
        try:
            item = await asyncio.wait_for(self.queue.get(), timeout=0.1)
            self.process_count += 1

            # Try to drain buffer if queue has space
            if not self.buffer.empty() and not self.queue.full():
                try:
                    buffered_item = self.buffer.get_nowait()
                    await self.queue.put(buffered_item)
                except asyncio.QueueEmpty:
                    pass

            return item
        except asyncio.TimeoutError:
            return None

    async def get_metrics(self) -> BackpressureMetrics:
        """Get backpressure metrics.

        Returns:
            BackpressureMetrics object
        """
        elapsed = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        processing_rate = self.process_count / elapsed if elapsed > 0 else 0
        drop_rate = self.drop_count / elapsed if elapsed > 0 else 0

        # Estimate latency based on queue size
        latency_ms = (self.queue.qsize() / processing_rate * 1000) if processing_rate > 0 else 0

        return BackpressureMetrics(
            queue_size=self.queue.qsize(),
            processing_rate=processing_rate,
            drop_rate=drop_rate,
            latency_ms=latency_ms,
            timestamp=datetime.now(timezone.utc),
        )

    def is_under_pressure(self) -> bool:
        """Check if system is under backpressure.

        Returns:
            True if under pressure
        """
        return self.queue.qsize() >= (self.max_queue_size * 0.8)

    async def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self.drop_count = 0
        self.process_count = 0
        self.start_time = datetime.now(timezone.utc)
