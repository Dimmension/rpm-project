from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import KeyBuilder
from redis.asyncio import Redis

from config.settings import settings
from src.handlers.command.router import router as command_router
from src.handlers.message.router import router as message_router


class CustomKeyBuilder(KeyBuilder):
    def __init__(self, prefix: str = "fsm"):
        self.prefix = prefix

    def build(self, key: str, destiny: str) -> str:
        return f"{self.prefix}:{key}:{destiny}"


storage = RedisStorage(
    redis=Redis(
        host='redis',
        port=6379,
        db=0
    ),
    key_builder=CustomKeyBuilder(prefix="fsm")
)

dp = Dispatcher(storage=storage)
default = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=settings.BOT_TOKEN, default=default)

dp.include_router(command_router)
dp.include_router(message_router)
