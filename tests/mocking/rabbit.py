import asyncio
import contextlib
import uuid
from collections import deque
from dataclasses import dataclass
from typing import Iterator
from unittest.mock import AsyncMock

import aio_pika
from aio_pika.exceptions import QueueEmpty


@dataclass
class MockChannelPool:  # -> Channel
    channel: 'MockChannel'

    def acquire(self):
        return self.channel


@dataclass
class MockChannel:
    queue: 'MockQueue'
    exchange: 'MockExchange'

    def __aenter__(self) -> 'MockChannel':
        return self

    def __await__(self) -> 'MockChannel':
        yield
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        return self

    async def set_qos(self, *args, **kwargs) -> None:
        return

    async def declare_queue(self, *args, **kwargs) -> 'MockQueue':
        return self.queue

    async def declare_exchange(self, *args, **kwargs) -> 'MockQueue':
        return self.exchange


class MockQueueIterator:
    def __init__(self, queue: deque['MockMessage']):
        self.queue: Iterator['MockMessage'] = iter(queue)

    def __aiter__(self):
        return self

    async def __anext__(self) -> 'MockMessage':
        return next(self.queue)

    def __aenter__(self) -> 'MockQueueIterator':
        return self

    def __await__(self) -> 'MockQueueIterator':
        yield
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb) -> 'MockQueueIterator':
        return self


@dataclass
class MockQueue:
    queue: deque['MockMessage']

    async def get(self, *args, **kwargs) -> 'MockMessage':
        try:
            return self.queue.popleft()
        except IndexError:
            raise QueueEmpty

    def iterator(self) -> MockQueueIterator:
        return MockQueueIterator(queue=self.queue)

    async def put(self, value: bytes, correlation_id) -> None:
        self.queue.append(MockMessage(body=value, correlation_id=correlation_id))


class MockMessageProcess:
    def __aenter__(self) -> 'MockQueueIterator':
        return self

    def __await__(self) -> 'MockQueueIterator':
        yield
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb) -> 'MockQueueIterator':
        return self


@dataclass
class MockMessage:
    body: bytes
    correlation_id: str

    def process(self) -> MockMessageProcess:
        return MockMessageProcess()


class MockExchange(AsyncMock):
    ...



class MockExchangeMessage(aio_pika.Message):
    def __eq__(self, other):
        return self.body == other.body
