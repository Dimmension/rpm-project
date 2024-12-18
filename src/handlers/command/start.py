from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup

from src.handlers import buttons
from src.handlers.states.auth import AuthGroup

from .router import router


@router.message(Command('start'))
async def start_cmd(message: Message, state: FSMContext) -> None:
    await state.set_state(AuthGroup.authorized)
    markup = ReplyKeyboardMarkup(
        keyboard=[[buttons.settings]],
        resize_keyboard=True,
    )
    await message.answer(
        'Вы можете делать чудеса!!!',
        reply_markup=markup,
    )


# @router.message(Command('start'))
# async def start_cmd(message: Message, state: FSMContext) -> None:
#     await state.set_state(AuthGroup.no_authorized)
#     markup = InlineKeyboardMarkup(inline_keyboard=[[buttons.auth]])
#     await message.answer(
#         'Вам необходимо авторизоваться!',
#         reply_markup=markup,
#     )
