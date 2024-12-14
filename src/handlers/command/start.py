import logging
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup

from src.handlers import buttons
from src.handlers.states.auth import AuthGroup
from src.logger import logger, LOGGING_CONFIG

from .router import router

logging.config.dictConfig(LOGGING_CONFIG)


@router.message(Command('start'))
async def start_cmd(message: Message, state: FSMContext) -> None:
    logger.info(f'User {message.user_from} started conversation with bot!')
    await state.set_state(AuthGroup.no_authorized)
    markup = InlineKeyboardMarkup(inline_keyboard=[[buttons.auth]])
    await message.answer(
        'Вам необходимо авторизоваться!',
        reply_markup=markup,
    )
