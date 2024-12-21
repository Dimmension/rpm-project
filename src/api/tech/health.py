import asyncio
import random
import time
from asyncio import Task
from typing import Any

import aio_pika
import msgpack
from aio_pika import ExchangeType
from aiogram.methods.base import TelegramType, TelegramMethod
from aiogram.types import Update
from fastapi.responses import ORJSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette_context import context
from starlette_context.header_keys import HeaderKeys

from src.api.tech.router import router
from src.bg_tasks import background_tasks
from src.bot import get_dp, get_bot
from src.logger import logger
from src.metrics import TOTAL_REQ, LATENCY, TOTAL_SEND_MESSAGES
from storage.rabbit import channel_pool


@router.get("/send")
async def send(
    request: Request,
) -> Response:
    text = '_'.join([str(random.randint(0, 100)) for _ in range(10)])
    TOTAL_SEND_MESSAGES.inc()
    await publish({'text': text})
    return Response()


queue_name = 'user_messages'


async def publish(body: dict[str, any]) -> None:
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange("first_exchange", ExchangeType.TOPIC, durable=True)  # !
        logger.info('Publishing message...')

        queue = await channel.declare_queue(queue_name, durable=True)

        # Binding queue
        await queue.bind(exchange, queue_name)

        await exchange.publish(
            aio_pika.Message(msgpack.packb(body), correlation_id=context.get(HeaderKeys.correlation_id)),
            queue_name
        )