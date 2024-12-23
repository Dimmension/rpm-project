import asyncio
from collections import deque
import contextlib
from pathlib import Path
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock

import aio_pika
import msgpack
from neo4j import AsyncTransaction
import pytest
import pytest_asyncio

from scripts.load_fixture import load_fixture
from src import bot
from storage import rabbit, db
from tests.mocking.rabbit import MockQueue, MockChannelPool, MockChannel, MockExchange, MockExchangeMessage
from storage.db import driver


@pytest_asyncio.fixture(autouse=True)
async def db_session(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[AsyncTransaction, None]:
    async with driver.session() as session:
        tx = await session.begin_transaction()

        @contextlib.asynccontextmanager
        async def overrided_session():
            yield tx

        monkeypatch.setattr(db.driver, 'session', overrided_session)

        yield tx
        await session.close()


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def _load_seeds(db_session, seeds: list[Path]) -> None:
    await load_fixture(seeds, db_session)


@pytest.fixture(autouse=True)
def mock_bot_dp(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    mock = AsyncMock()
    monkeypatch.setattr(bot, 'dp', mock)
    return mock


@pytest.fixture()
def mock_exchange() -> MockExchange:
    return MockExchange()


@pytest_asyncio.fixture()
async def _load_queue(monkeypatch: pytest.MonkeyPatch, predefined_queue: Any, mock_exchange: MockExchange):
    queue = MockQueue(deque())

    if predefined_queue is not None:
        await queue.put(msgpack.packb(predefined_queue))

    channel = MockChannel(queue=queue, exchange=mock_exchange)
    pool = MockChannelPool(channel=channel)
    monkeypatch.setattr(rabbit, 'channel_pool', pool)
    monkeypatch.setattr(aio_pika, 'Message', MockExchangeMessage)
