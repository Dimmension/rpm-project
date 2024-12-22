import asyncio
from asyncio import Task
from typing import Any

from aiogram.methods.base import TelegramMethod
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.responses import JSONResponse

from src import bot
from src.api.tg.router import router
from src.bg_tasks import background_tasks


@router.post('/webhook')
async def webhook(request: Request) -> JSONResponse:
    update = await request.json()

    task: Task[TelegramMethod[Any] | None] = asyncio.create_task(
        bot.dp.feed_webhook_update(bot.bot, update),
    )
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    return ORJSONResponse({'status': 'ok'})
