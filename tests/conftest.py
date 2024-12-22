import asyncio
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import aio_pika
import msgpack
import pytest
import pytest_asyncio
from fastapi import FastAPI
from mocking.rabbit import (MockChannel, MockChannelPool, MockExchange,
                            MockExchangeMessage, MockQueue)

from scripts.load_fixture import load_fixture
from src import bot
from src.app import create_app
from storage import db
from storage import db as consumer_db
from storage import rabbit
from storage import rabbit as consumer_rabbit
from storage.db import driver


@pytest.fixture(scope="session")
def event_loop():
    """Создаем новый событийный цикл для тестов."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='session')
def app() -> FastAPI:
    return create_app()

@asynccontextmanager
async def get_neo4j_session():
    async with driver.session() as session:
        try:
            yield session
        finally:
            await driver.close()

@pytest_asyncio.fixture()
async def db_session(app: FastAPI):
    async with driver.session() as session:
        async def override_neo4j_session():
            yield session

        app.dependency_overrides[get_neo4j_session] = override_neo4j_session

        yield session

    await driver.close()


@pytest_asyncio.fixture()
async def _load_seeds(db_session, seeds: list[Path]) -> None:
    await load_fixture(seeds, db_session)

@pytest.fixture
def correlation_id():
    return 1

@pytest_asyncio.fixture(autouse=True)
async def neo4j_session(app: FastAPI, monkeypatch):
    async with driver.session() as session:
        async def override_neo4j_session():
            yield session

        monkeypatch.setattr(consumer_db, "driver", session)
        monkeypatch.setattr(db, "driver", session)

        app.dependency_overrides[get_neo4j_session] = override_neo4j_session

        yield session

    await driver.close()


@pytest.fixture(autouse=True)
def mock_bot_dp(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    mock = AsyncMock()
    monkeypatch.setattr(bot, 'dp', mock) # bot.dp -> mock
    return mock

@pytest.fixture()
def mock_exchange() -> MockExchange:
    return MockExchange()




@pytest.fixture()
def mock_exchange() -> MockExchange:  # noqa: F811
    return MockExchange()


@pytest_asyncio.fixture()
async def _load_queue(monkeypatch: pytest.MonkeyPatch, predefined_queue: Any, correlation_id, mock_exchange: MockExchange):

    queue = MockQueue(deque())

    if predefined_queue is not None:
        await queue.put(msgpack.packb(predefined_queue), correlation_id=1)
    channel = MockChannel(queue=queue, exchange=mock_exchange)
    pool = MockChannelPool(channel=channel)
    monkeypatch.setattr(rabbit, 'channel_pool', pool)
    monkeypatch.setattr(consumer_rabbit, 'channel_pool', pool)
    monkeypatch.setattr(aio_pika, 'Message', MockExchangeMessage)
