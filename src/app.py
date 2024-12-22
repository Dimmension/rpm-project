import asyncio

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn

from fastapi import FastAPI
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from config.settings import settings
from src.api.tg.router import router as tg_router
from src.bot import dp, bot
from src.bg_tasks import background_tasks


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    wh_info = await bot.get_webhook_info()
    if wh_info.url != settings.BOT_WEBHOOK_URL:
        await bot.set_webhook(settings.BOT_WEBHOOK_URL)

    yield

    while background_tasks:
        await asyncio.sleep(0)

    await bot.delete_webhook()


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/swagger', lifespan=lifespan)
    app.include_router(tg_router, prefix='/tg', tags=['tg'])

    app.add_middleware(
        RawContextMiddleware,
        plugins=[plugins.CorrelationIdPlugin()],
    )
    return app


async def start_pooling():
    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == '__main__':
    if settings.BOT_WEBHOOK_URL:
        uvicorn.run(
            'src.app:create_app',
            factory=True,
            host='0.0.0.0',
            port=8000,
            workers=1,
        )
    else:
        asyncio.run(start_pooling())
