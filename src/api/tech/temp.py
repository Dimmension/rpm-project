import asyncio
import random
import time
from asyncio import Task
from typing import Any
from aiogram.methods.base import TelegramType, TelegramMethod
from aiogram.types import Update
from fastapi.responses import ORJSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from src.api.tech.router import router
from src.bg_tasks import background_tasks
from src.bot import get_dp, get_bot
from src.metrics import TOTAL_REQ, LATENCY
@router.get("/health")
async def health(
    request: Request,
) -> Response:
    start = time.monotonic()
    sleep_time = random.randint(0, 20) / 10
    await asyncio.sleep(sleep_time)
    end = time.monotonic()
    LATENCY.labels("health").observe(end - start)
    return Response()