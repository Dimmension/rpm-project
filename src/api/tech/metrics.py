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
@router.get("/metrics")
async def metrics(
    request: Request,
) -> Response:
    return Response(generate_latest(), headers={'Content-Type': CONTENT_TYPE_LATEST})