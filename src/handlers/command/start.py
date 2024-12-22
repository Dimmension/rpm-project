import logging

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from src.handlers import buttons
from src.handlers.markups import menu
from src.handlers.states.auth import AuthGroup
from src.logger import LOGGING_CONFIG, logger

from .router import router

logging.config.dictConfig(LOGGING_CONFIG)


@router.message(Command('start'), AuthGroup.authorized)
async def start_cmd(message: Message, state: FSMContext) -> None:
    # await state.set_state(AuthGroup.authorized)
    await message.answer(
        'Вы можете делать чудеса!!!',
        reply_markup=menu,
    )


@router.message(Command('start'))
async def start_cmd(message: Message, state: FSMContext) -> None:  # noqa: F811
    logger.info(f'User {message.from_user.username} started conversation with bot!')
    await state.set_state(AuthGroup.no_authorized)
    markup = InlineKeyboardMarkup(inline_keyboard=[[buttons.auth]])
    await message.answer(
        'Вам необходимо авторизоваться!',
        reply_markup=markup,
    )
