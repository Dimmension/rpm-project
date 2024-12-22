import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from config.settings import settings
from src.logger import LOGGING_CONFIG, logger
from src.api.dat.router import router as data_router
from src.api.tg.router import router as tg_router
from src.bg_tasks import background_tasks
from src.bot import bot, dp


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info('Starting producer lifespan')

    wh_info = await bot.get_webhook_info()
    if wh_info.url != settings.BOT_WEBHOOK_URL:
        await bot.set_webhook(settings.BOT_WEBHOOK_URL)
        logger.info('--Webhook initialized--')

    yield

    while background_tasks:
        await asyncio.sleep(0)

    await bot.delete_webhook()
    logger.info('Ending app lifespan')
    return


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/swagger', lifespan=lifespan)
    app.include_router(tg_router, prefix='/tg', tags=['tg'])
    app.include_router(data_router, prefix='', tags=['dat'])
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
            port=8001,
            workers=1,
        )
        logger.info('Bot started on Webhook')
    else:
        asyncio.run(start_pooling())
        logger.info('Bot started on polling')