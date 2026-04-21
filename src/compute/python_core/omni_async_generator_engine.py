"""
OMNI Async Generator Engine
===========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI ASYNC GENERATOR ENGINE (SEMESTER 3 — BATCH 38.6)
# ===========================================================================
# Absorbed From  : asyncio + aiohttp + trio + anyio patterns
# Logic Inherited: Python / Compute Layer (Async Generators & Streams)
# ===========================================================================
#
# By studying asyncio and trio, Mother learned async iteration patterns:
#   1. async for consumes async generators/iterators
#   2. asyncio.Queue enables producer-consumer streams
#   3. Backpressure via bounded queues prevents memory overflow
#   4. Fan-out/fan-in patterns for parallel stream processing
#   5. Async context managers for resource cleanup

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import (
    Any, AsyncGenerator, AsyncIterator, Awaitable, Callable, Dict,
    Generic, List, Optional, TypeVar,
)

T = TypeVar("T")
U = TypeVar("U")


# ============================================================
# PART 1: Async Stream Primitives
# ============================================================

class AsyncStream(Generic[T]):
    """Async stream with map/filter/take/batch combinators."""

    def __init__(self, source: AsyncGenerator[T, None]):
        """Initialize AsyncStream."""
        self._source = source
        self._total_emitted = 0

    def __aiter__(self) -> AsyncIterator[T]:
        return self._iterate()

    async def _iterate(self) -> AsyncGenerator[T, None]:
        async for item in self._source:
            self._total_emitted += 1
            yield item

    def map(self, func: Callable[[T], U]) -> "AsyncStream[U]":
        """Transform each element."""
        source = self._source

        async def mapped() -> AsyncGenerator[U, None]:
            async for item in source:
                yield func(item)

        return AsyncStream(mapped())

    def filter(self, predicate: Callable[[T], bool]) -> "AsyncStream[T]":
        """Keep only elements matching predicate."""
        source = self._source

        async def filtered() -> AsyncGenerator[T, None]:
            async for item in source:
                if predicate(item):
                    yield item

        return AsyncStream(filtered())

    def take(self, n: int) -> "AsyncStream[T]":
        """Take first n elements."""
        source = self._source

        async def taken() -> AsyncGenerator[T, None]:
            count = 0
            async for item in source:
                if count >= n:
                    break
                yield item
                count += 1

        return AsyncStream(taken())

    def batch(self, size: int) -> "AsyncStream[List[T]]":
        """Group elements into batches."""
        source = self._source

        async def batched() -> AsyncGenerator[List[T], None]:
            batch: List[T] = []
            async for item in source:
                batch.append(item)
                if len(batch) >= size:
                    yield batch
                    batch = []
            if batch:
                yield batch

        return AsyncStream(batched())

    def flat_map(self, func: Callable[[T], AsyncGenerator[U, None]]) -> "AsyncStream[U]":
        """Map and flatten async generators."""
        source = self._source

        async def flat_mapped() -> AsyncGenerator[U, None]:
            async for item in source:
                async for sub_item in func(item):
                    yield sub_item

        return AsyncStream(flat_mapped())

    async def collect(self) -> List[T]:
        """Consume stream into a list."""
        result: List[T] = []
        async for item in self:
            result.append(item)
        return result

    async def reduce(self, func: Callable[[T, T], T], initial: T) -> T:
        """Reduce stream to a single value."""
        accumulator = initial
        async for item in self:
            accumulator = func(accumulator, item)
        return accumulator

    async def for_each(self, func: Callable[[T], Any]) -> int:
        """Apply function to each element, return count."""
        count = 0
        async for item in self:
            func(item)
            count += 1
        return count

    @staticmethod
    def from_iterable(iterable) -> "AsyncStream":
        """Create stream from sync iterable."""
        async def gen():
            for item in iterable:
                yield item
        return AsyncStream(gen())

    @staticmethod
    def from_range(start: int, stop: int, step: int = 1) -> "AsyncStream[int]":
        """Create stream from range."""
        async def gen():
            i = start
            while i < stop:
                yield i
                i += step
        return AsyncStream(gen())

    @staticmethod
    def interval(seconds: float, count: Optional[int] = None) -> "AsyncStream[int]":
        """Emit incrementing integers at fixed intervals."""
        async def gen():
            i = 0
            while count is None or i < count:
                await asyncio.sleep(seconds)
                yield i
                i += 1
        return AsyncStream(gen())


# ============================================================
# PART 2: Bounded Async Channel (Backpressure)
# ============================================================

class AsyncChannel(Generic[T]):
    """Bounded async channel with backpressure support."""

    def __init__(self, capacity: int = 64):
        """Initialize AsyncChannel."""
        self._queue: asyncio.Queue[Optional[T]] = asyncio.Queue(maxsize=capacity)
        self._capacity = capacity
        self._closed = False
        self._total_sent = 0
        self._total_received = 0

    async def send(self, value: T) -> None:
        """Send value. Blocks if channel is full (backpressure)."""
        if self._closed:
            raise RuntimeError("Cannot send to closed channel")
        await self._queue.put(value)
        self._total_sent += 1

    async def receive(self) -> Optional[T]:
        """Receive value. Returns None when channel is closed and empty."""
        value = await self._queue.get()
        if value is None and self._closed:
            return None
        self._total_received += 1
        return value

    async def close(self) -> None:
        """Close the channel. No more sends allowed."""
        self._closed = True
        await self._queue.put(None)  # Sentinel

    def __aiter__(self) -> AsyncIterator[T]:
        return self._iterate()

    async def _iterate(self) -> AsyncGenerator[T, None]:
        while True:
            value = await self.receive()
            if value is None:
                break
            yield value

    def to_stream(self) -> AsyncStream[T]:
        """Convert channel to async stream."""
        return AsyncStream(self._iterate())

    @property
    def pending(self) -> int:
        """Execute pending operation for AsyncChannel."""
        return self._queue.qsize()

    @property
    def is_full(self) -> bool:
        """Check if full condition holds."""
        return self._queue.full()

    @property
    def is_empty(self) -> bool:
        """Check if empty condition holds."""
        return self._queue.empty()


# ============================================================
# PART 3: Fan-Out / Fan-In
# ============================================================

async def fan_out(
    stream: AsyncStream[T],
    workers: int,
    processor: Callable[[T], Awaitable[U]],
) -> List[U]:
    """Distribute stream items across multiple worker tasks."""
    channel = AsyncChannel[T](capacity=workers * 2)
    results: List[U] = []
    results_lock = asyncio.Lock()

    async def worker_task():
        async for item in channel:
            result = await processor(item)
            async with results_lock:
                results.append(result)

    # Start workers
    workers_list = [asyncio.create_task(worker_task()) for _ in range(workers)]

    # Feed items
    async for item in stream:
        await channel.send(item)
    await channel.close()

    # Wait for workers
    await asyncio.gather(*workers_list)
    return results


async def fan_in(*streams: AsyncStream[T]) -> AsyncStream[T]:
    """Merge multiple streams into one."""
    channel = AsyncChannel[T](capacity=128)

    async def feed(stream: AsyncStream[T]):
        async for item in stream:
            await channel.send(item)

    async def run():
        tasks = [asyncio.create_task(feed(s)) for s in streams]
        await asyncio.gather(*tasks)
        await channel.close()

    asyncio.ensure_future(run())
    return channel.to_stream()


# ============================================================
# Diagnostics
# ============================================================
