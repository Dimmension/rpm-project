
import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from src.app import create_app


@pytest.fixture(scope='session')
def app() -> FastAPI:
    return create_app()



@pytest_asyncio.fixture(scope='session')
async def http_client(app: FastAPI) -> httpx.AsyncClient:
    async with LifespanManager(app):
        async with httpx.AsyncClient(app=app, base_url='http://localhost') as client:
            yield client
