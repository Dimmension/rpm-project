import asyncio
import logging.config
from typing import AsyncGenerator

from fastapi import FastAPI
from consumer.app import start_consumer
from logger import LOGGING_CONFIG, logger


async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info('Starting app lifespan')
    task = asyncio.create_task(start_consumer())
    yield
    task.cancel()


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/swagger', lifespan=lifespan)
    return app
