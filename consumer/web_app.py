import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI
from consumer.app import start_consumer


async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    task = asyncio.create_task(start_consumer())
    yield
    task.cancel()


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/swagger', lifespan=lifespan)
    return app
