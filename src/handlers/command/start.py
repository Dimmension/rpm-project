from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup
import msgpack

from consumer.schema.recommendation import RecMessage
from src.handlers import buttons
from src.handlers.markups import menu
from src.handlers.states.auth import AuthGroup
from storage import consts
from storage.rabbit import send_msg

from .router import router


@router.message(Command('start'), AuthGroup.authorized)
async def start_cmd(message: Message, state: FSMContext) -> None:
    # await state.set_state(AuthGroup.authorized)
    await message.answer(
        'Вы можете делать чудеса!!!',
        reply_markup=menu,
    )


@router.message(Command('start'))
async def start_cmd(message: Message, state: FSMContext) -> None:
    await state.set_state(AuthGroup.no_authorized)
    markup = InlineKeyboardMarkup(inline_keyboard=[[buttons.auth]])
    await message.answer(
        'Вам необходимо авторизоваться!',
        reply_markup=markup,
    )
